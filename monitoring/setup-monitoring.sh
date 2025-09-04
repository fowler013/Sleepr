#!/bin/bash

# Sleepr Monitoring Setup Script
# This script sets up comprehensive monitoring for the Sleepr application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
MONITORING_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$MONITORING_DIR")"
ENV_FILE="$PROJECT_ROOT/.env.monitoring"

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create environment file if it doesn't exist
create_env_file() {
    print_status "Creating monitoring environment configuration..."
    
    if [ ! -f "$ENV_FILE" ]; then
        cat > "$ENV_FILE" << EOF
# Sleepr Monitoring Configuration
ENVIRONMENT=development

# Grafana Configuration
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin123
GRAFANA_SECRET_KEY=SW2YcwTIb9zpOOhoPsMm
GRAFANA_DOMAIN=localhost
GRAFANA_ROOT_URL=http://localhost:3001

# Email Alerts Configuration
SMTP_HOST=localhost:587
SMTP_USERNAME=
SMTP_PASSWORD=
ALERT_FROM_EMAIL=alerts@sleepr.local
DEFAULT_ALERT_EMAIL=admin@sleepr.local
CRITICAL_ALERT_EMAIL=admin@sleepr.local
WARNING_ALERT_EMAIL=admin@sleepr.local
BUSINESS_ALERT_EMAIL=business@sleepr.local

# Slack Configuration
SLACK_WEBHOOK_URL=

# Database Configuration
POSTGRES_EXPORTER_URI=postgresql://sleepr_user:password@postgres:5432/sleepr?sslmode=disable

# Redis Configuration
REDIS_ADDR=redis:6379
REDIS_PASSWORD=redispassword
EOF
        print_status "Created monitoring environment file at $ENV_FILE"
    else
        print_status "Monitoring environment file already exists"
    fi
}

# Create additional configuration files
create_configs() {
    print_status "Creating additional monitoring configurations..."
    
    # Blackbox exporter config
    mkdir -p "$MONITORING_DIR/blackbox"
    cat > "$MONITORING_DIR/blackbox/blackbox.yml" << EOF
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: [200, 201, 202, 204, 301, 302]
      method: GET
      headers:
        Host: localhost
        User-Agent: "Blackbox Exporter"
      no_follow_redirects: false
      fail_if_ssl: false
      fail_if_not_ssl: false
      tls_config:
        insecure_skip_verify: false
      preferred_ip_protocol: "ip4"

  http_post_2xx:
    prober: http
    timeout: 5s
    http:
      method: POST
      headers:
        Content-Type: application/json
      body: '{"health": "check"}'

  tcp_connect:
    prober: tcp
    timeout: 5s

  pop3s_banner:
    prober: tcp
    timeout: 5s
    tcp:
      query_response:
        - expect: "^+OK"
      tls: true
      tls_config:
        insecure_skip_verify: false

  ssh_banner:
    prober: tcp
    timeout: 5s
    tcp:
      query_response:
        - expect: "^SSH-2.0-"

  irc_banner:
    prober: tcp
    timeout: 5s
    tcp:
      query_response:
        - send: "NICK prober"
        - send: "USER prober prober prober :prober"
        - expect: "PING :([^ ]+)"
          send: "PONG :\1"
        - expect: "^:[^ ]+ 001"

  icmp:
    prober: icmp
    timeout: 5s
    icmp:
      preferred_ip_protocol: "ip4"
EOF

    # Postgres exporter queries
    mkdir -p "$MONITORING_DIR/postgres-exporter"
    cat > "$MONITORING_DIR/postgres-exporter/queries.yml" << EOF
pg_replication:
  query: "SELECT CASE WHEN NOT pg_is_in_recovery() THEN 0 ELSE GREATEST (0, EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))) END AS lag"
  master: true
  metrics:
    - lag:
        usage: "GAUGE"
        description: "Replication lag behind master in seconds"

pg_postmaster:
  query: "SELECT pg_postmaster_start_time as start_time_seconds from pg_postmaster_start_time()"
  master: true
  metrics:
    - start_time_seconds:
        usage: "GAUGE"
        description: "Time at which postmaster started"

pg_stat_user_tables:
  query: "SELECT schemaname, tablename, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch, n_tup_ins, n_tup_upd, n_tup_del, n_tup_hot_upd, n_live_tup, n_dead_tup, n_mod_since_analyze, last_vacuum, last_autovacuum, last_analyze, last_autoanalyze, vacuum_count, autovacuum_count, analyze_count, autoanalyze_count FROM pg_stat_user_tables"
  metrics:
    - schemaname:
        usage: "LABEL"
        description: "Name of the schema that this table is in"
    - tablename:
        usage: "LABEL"
        description: "Name of this table"
    - seq_scan:
        usage: "COUNTER"
        description: "Number of sequential scans initiated on this table"
    - seq_tup_read:
        usage: "COUNTER"
        description: "Number of live rows fetched by sequential scans"
    - idx_scan:
        usage: "COUNTER"
        description: "Number of index scans initiated on this table"
    - idx_tup_fetch:
        usage: "COUNTER"
        description: "Number of live rows fetched by index scans"
    - n_tup_ins:
        usage: "COUNTER"
        description: "Number of rows inserted"
    - n_tup_upd:
        usage: "COUNTER"
        description: "Number of rows updated"
    - n_tup_del:
        usage: "COUNTER"
        description: "Number of rows deleted"
    - n_tup_hot_upd:
        usage: "COUNTER"
        description: "Number of rows HOT updated"
    - n_live_tup:
        usage: "GAUGE"
        description: "Estimated number of live rows"
    - n_dead_tup:
        usage: "GAUGE"
        description: "Estimated number of dead rows"
    - n_mod_since_analyze:
        usage: "GAUGE"
        description: "Estimated number of rows changed since last analyze"
    - last_vacuum:
        usage: "GAUGE"
        description: "Last time at which this table was manually vacuumed"
    - last_autovacuum:
        usage: "GAUGE"
        description: "Last time at which this table was vacuumed by the autovacuum daemon"
    - last_analyze:
        usage: "GAUGE"
        description: "Last time at which this table was manually analyzed"
    - last_autoanalyze:
        usage: "GAUGE"
        description: "Last time at which this table was analyzed by the autovacuum daemon"
    - vacuum_count:
        usage: "COUNTER"
        description: "Number of times this table has been manually vacuumed"
    - autovacuum_count:
        usage: "COUNTER"
        description: "Number of times this table has been vacuumed by the autovacuum daemon"
    - analyze_count:
        usage: "COUNTER"
        description: "Number of times this table has been manually analyzed"
    - autoanalyze_count:
        usage: "COUNTER"
        description: "Number of times this table has been analyzed by the autovacuum daemon"
EOF

    # Loki configuration
    mkdir -p "$MONITORING_DIR/loki"
    cat > "$MONITORING_DIR/loki/local-config.yaml" << EOF
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

query_range:
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://localhost:9093

# By default, Loki will send anonymous, but uniquely-identifiable usage and configuration
# analytics to Grafana Labs. These statistics are sent to https://stats.grafana.org/
#
# Statistics help us better understand how Loki is used, and they show us performance
# levels for most users. This helps us prioritize features and documentation.
# For more information on what's sent, look at
# https://github.com/grafana/loki/blob/main/pkg/usagestats/stats.go
# Refer to the buildReport method to see what goes into a report.
#
# If you would like to disable reporting, uncomment the following lines:
#analytics:
#  reporting_enabled: false
EOF

    # Promtail configuration
    mkdir -p "$MONITORING_DIR/promtail"
    cat > "$MONITORING_DIR/promtail/config.yml" << EOF
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: containers
    static_configs:
      - targets:
          - localhost
        labels:
          job: containerlogs
          __path__: /var/lib/docker/containers/*/*log

    pipeline_stages:
      - json:
          expressions:
            output: log
            stream: stream
            attrs:
      - json:
          source: attrs
          expressions:
            tag:
      - regex:
          source: tag
          expression: (?P<container_name>(?:[^|]*/){2}(?P<container_name_only>[^|]*))
      - timestamp:
          source: time
          format: RFC3339Nano
      - labels:
          stream:
          container_name:
          container_name_only:
      - output:
          source: output

  - job_name: syslog
    static_configs:
      - targets:
          - localhost
        labels:
          job: syslog
          __path__: /var/log/syslog

  - job_name: auth
    static_configs:
      - targets:
          - localhost
        labels:
          job: auth
          __path__: /var/log/auth.log
EOF

    print_status "Created additional monitoring configurations"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Start monitoring services
start_monitoring() {
    print_status "Starting monitoring services..."
    
    cd "$MONITORING_DIR"
    
    # Load environment variables
    if [ -f "$ENV_FILE" ]; then
        export $(cat "$ENV_FILE" | xargs)
    fi
    
    # Start services
    docker-compose -f docker-compose.monitoring.yml up -d
    
    print_status "Monitoring services started successfully"
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    check_service_health
}

# Stop monitoring services
stop_monitoring() {
    print_status "Stopping monitoring services..."
    
    cd "$MONITORING_DIR"
    docker-compose -f docker-compose.monitoring.yml down
    
    print_status "Monitoring services stopped"
}

# Check service health
check_service_health() {
    print_status "Checking service health..."
    
    services=(
        "http://localhost:9090/-/healthy:Prometheus"
        "http://localhost:9093/-/healthy:AlertManager"
        "http://localhost:3001/api/health:Grafana"
        "http://localhost:9100/metrics:Node Exporter"
        "http://localhost:9115/metrics:Blackbox Exporter"
        "http://localhost:3100/ready:Loki"
    )
    
    for service in "${services[@]}"; do
        url="${service%:*}"
        name="${service#*:}"
        
        if curl -f -s "$url" > /dev/null 2>&1; then
            print_status "✅ $name is healthy"
        else
            print_warning "⚠️  $name is not responding"
        fi
    done
}

# Display service URLs
show_services() {
    print_status "Monitoring Services:"
    echo ""
    echo "🔍 Prometheus (Metrics): http://localhost:9090"
    echo "📊 Grafana (Dashboards): http://localhost:3001"
    echo "🚨 AlertManager (Alerts): http://localhost:9093"
    echo "💾 Loki (Logs): http://localhost:3100"
    echo ""
    echo "📈 Default Grafana Login:"
    echo "   Username: admin"
    echo "   Password: admin123"
    echo ""
    echo "🎯 Pre-configured Dashboards:"
    echo "   • API Overview"
    echo "   • Analytics & ML Performance"
    echo "   • Infrastructure & System Metrics"
    echo "   • Business Metrics & User Analytics"
    echo ""
}

# Main execution
main() {
    case "${1:-start}" in
        "start")
            print_status "Setting up Sleepr monitoring stack..."
            check_prerequisites
            create_env_file
            create_configs
            start_monitoring
            show_services
            ;;
        "stop")
            stop_monitoring
            ;;
        "restart")
            stop_monitoring
            sleep 5
            start_monitoring
            show_services
            ;;
        "status")
            check_service_health
            ;;
        "logs")
            cd "$MONITORING_DIR"
            docker-compose -f docker-compose.monitoring.yml logs -f "${2:-}"
            ;;
        "clean")
            print_status "Cleaning up monitoring stack..."
            cd "$MONITORING_DIR"
            docker-compose -f docker-compose.monitoring.yml down -v
            docker system prune -f
            print_status "Monitoring stack cleaned"
            ;;
        *)
            echo "Usage: $0 {start|stop|restart|status|logs|clean}"
            echo ""
            echo "Commands:"
            echo "  start    - Start monitoring services (default)"
            echo "  stop     - Stop monitoring services"
            echo "  restart  - Restart monitoring services"
            echo "  status   - Check service health"
            echo "  logs     - Show service logs (optionally specify service name)"
            echo "  clean    - Remove all containers and volumes"
            exit 1
            ;;
    esac
}

main "$@"
