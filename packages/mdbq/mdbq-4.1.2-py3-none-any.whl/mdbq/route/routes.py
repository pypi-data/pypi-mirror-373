"""
管理路由API

主要功能：
1. 实时监控面板
2. 统计数据查看
3. 告警信息展示
4. 报告生成
5. 数据清理管理

"""

from flask import Blueprint, jsonify, request, render_template_string
from datetime import datetime, timedelta
from mdbq.route.monitor import route_monitor, monitor_request, get_request_id
from mdbq.route.analytics import (
    get_realtime_metrics, get_traffic_trend, get_endpoint_analysis,
    get_user_behavior_analysis, get_performance_alerts, generate_daily_report
)
import json

# 创建监控管理蓝图
monitor_bp = Blueprint('monitor', __name__, url_prefix='/admin/monitor')


@monitor_bp.route('/', methods=['GET'])
@monitor_request
def monitor_ui():
    """监控面板可视化界面（前端页面）"""
    return render_template_string("""
<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>API监控面板</title>
  <style>
    :root { --bg:#0b1220; --card:#111a2b; --text:#e6edf3; --sub:#a0a8b3; --ok:#16a34a; --warn:#f59e0b; --err:#ef4444; --muted:#22304a; }
    * { box-sizing: border-box; }
    body { margin:0; font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial; background: var(--bg); color: var(--text); }
    header { padding: 16px 24px; border-bottom: 1px solid var(--muted); display:flex; align-items:center; justify-content:space-between; }
    header h1 { margin: 0; font-size: 18px; }
    .wrap { padding: 20px; max-width: 1200px; margin: 0 auto; }
    .grid { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 16px; }
    .card { background: var(--card); border: 1px solid var(--muted); border-radius: 12px; padding: 16px; }
    .kpi { font-size: 12px; color: var(--sub); margin-bottom: 6px; }
    .val { font-size: 22px; font-weight: 700; }
    .row { display:flex; gap: 16px; margin-top: 16px; }
    .row .card { flex: 1; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th, td { border-bottom: 1px solid var(--muted); padding: 8px 6px; text-align: left; }
    th { color: var(--sub); font-weight: 600; }
    .badge { display:inline-block; padding:2px 8px; border-radius: 999px; font-size: 12px; }
    .badge.ok { background:#14351f; color:#4ade80; }
    .badge.warn { background:#3a2f16; color:#facc15; }
    .badge.err { background:#3b1112; color:#fda4af; }
    .muted { color: var(--sub); }
    .controls { display:flex; gap:10px; align-items:center; }
    input, select, button { background: #0e1626; color: var(--text); border:1px solid var(--muted); padding:8px 10px; border-radius: 8px; }
    button.primary { background: #1f2937; border-color:#2b3a55; cursor:pointer; }
    button.primary:hover { background:#263349; }
    .footer { color: var(--sub); font-size: 12px; margin-top: 12px; }
    @media (max-width: 960px) { .grid { grid-template-columns: repeat(2, minmax(0,1fr)); } }
    @media (max-width: 640px) { .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <h1>API监控面板</h1>
    <div class=\"controls\">
      <label class=\"muted\">自动刷新</label>
      <select id=\"autoRefresh\">
        <option value=\"0\">关闭</option>
        <option value=\"15\">15s</option>
        <option value=\"30\" selected>30s</option>
        <option value=\"60\">60s</option>
      </select>
      <button class=\"primary\" id=\"refreshBtn\">立即刷新</button>
    </div>
  </header>
  <div class=\"wrap\">
    <section class=\"grid\">
      <div class=\"card\"><div class=\"kpi\">近1小时请求数</div><div class=\"val\" id=\"k_requests_hour\">-</div></div>
      <div class=\"card\"><div class=\"kpi\">近24小时请求数</div><div class=\"val\" id=\"k_requests_day\">-</div></div>
      <div class=\"card\"><div class=\"kpi\">平均响应时间(ms)</div><div class=\"val\" id=\"k_avg_rt\">-</div></div>
      <div class=\"card\"><div class=\"kpi\">错误率(%)</div><div class=\"val\" id=\"k_err_rate\">-</div></div>
    </section>

    <div class=\"row\">
      <div class=\"card\">
        <h3 class=\"muted\">热门端点（近1小时）</h3>
        <table id=\"tbl_top_endpoints\"><thead><tr><th>端点</th><th>请求数</th><th>平均耗时(ms)</th></tr></thead><tbody></tbody></table>
      </div>
      <div class=\"card\">
        <h3 class=\"muted\">告警</h3>
        <table id=\"tbl_alerts\"><thead><tr><th>类型</th><th>级别</th><th>消息</th><th>时间</th></tr></thead><tbody></tbody></table>
      </div>
    </div>

    <div class=\"card\" style=\"margin-top:16px;\">
      <div style=\"display:flex; align-items:center; justify-content:space-between;\">
        <h3 class=\"muted\">流量趋势（日）</h3>
        <div class=\"controls\">
          <label class=\"muted\">天数</label>
          <select id=\"days\">
            <option value=\"7\" selected>7</option>
            <option value=\"14\">14</option>
            <option value=\"30\">30</option>
          </select>
        </div>
      </div>
      <table id=\"tbl_daily\"><thead><tr><th>日期</th><th>请求数</th><th>唯一IP</th><th>平均响应(ms)</th><th>错误数</th></tr></thead><tbody></tbody></table>
    </div>

    <div class=\"card\" style=\"margin-top:16px;\">
      <h3 class=\"muted\">请求搜索</h3>
      <div class=\"controls\" style=\"margin-bottom:10px; flex-wrap:wrap;\">
        <input id=\"q_endpoint\" placeholder=\"端点包含...\" style=\"min-width:200px;\" />
        <input id=\"q_client_ip\" placeholder=\"客户端IP\" />
        <select id=\"q_method\"><option value=\"\">方法</option><option>GET</option><option>POST</option><option>PUT</option><option>DELETE</option></select>
        <input id=\"q_status\" placeholder=\"状态码\" type=\"number\" style=\"width:120px;\" />
        <input id=\"q_min_rt\" placeholder=\"最小耗时(ms)\" type=\"number\" style=\"width:140px;\" />
        <button class=\"primary\" id=\"btn_search\">搜索</button>
      </div>
      <table id=\"tbl_requests\"><thead><tr><th>时间</th><th>请求ID</th><th>方法</th><th>端点</th><th>状态</th><th>耗时(ms)</th><th>IP</th></tr></thead><tbody></tbody></table>
      <div class=\"footer\" id=\"pg_info\"></div>
    </div>
  </div>

  <script>
    async function fetchJSON(url, options) {
      const res = await fetch(url, options);
      if (!res.ok) throw new Error('请求失败');
      const data = await res.json();
      if (data && data.data) return data.data;
      return data;
    }

    function setText(id, val) { document.getElementById(id).textContent = val ?? '-'; }

    async function loadRealtime() {
      const data = await fetchJSON('/admin/monitor/metrics/realtime');
      const m = data.realtime_metrics || {};
      setText('k_requests_hour', m.requests_per_hour ?? '-');
      setText('k_requests_day', m.requests_per_day ?? '-');
      setText('k_avg_rt', m.avg_response_time ?? '-');
      setText('k_err_rate', m.error_rate ?? '-');
      const tbody = document.querySelector('#tbl_top_endpoints tbody');
      tbody.innerHTML = '';
      (data.top_endpoints || []).forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${row.endpoint || '-'}</td><td>${row.request_count || 0}</td><td>${(row.avg_time||0).toFixed ? (row.avg_time||0).toFixed(2) : row.avg_time||0}</td>`;
        tbody.appendChild(tr);
      });
    }

    async function loadAlerts() {
      const data = await fetchJSON('/admin/monitor/alerts');
      const tbody = document.querySelector('#tbl_alerts tbody');
      tbody.innerHTML = '';
      (data.alerts || []).forEach(a => {
        const tr = document.createElement('tr');
        const sev = (a.severity||'').toUpperCase();
        const cls = sev === 'HIGH' ? 'err' : (sev === 'MEDIUM' ? 'warn' : 'ok');
        tr.innerHTML = `<td>${a.type||'-'}</td><td><span class=\"badge ${cls}\">${sev}</span></td><td>${a.message||'-'}</td><td>${a.timestamp||''}</td>`;
        tbody.appendChild(tr);
      });
    }

    async function loadTrend() {
      const days = document.getElementById('days').value || 7;
      const data = await fetchJSON(`/admin/monitor/traffic/trend?days=${days}`);
      const tbody = document.querySelector('#tbl_daily tbody');
      tbody.innerHTML = '';
      (data.daily_data || []).forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${r.date}</td><td>${r.requests}</td><td>${r.unique_ips}</td><td>${Number(r.avg_response_time||0).toFixed(2)}</td><td>${r.errors}</td>`;
        tbody.appendChild(tr);
      });
    }

    async function searchRequests(page=1, page_size=20) {
      const body = {
        page, page_size,
        filters: {
          endpoint: document.getElementById('q_endpoint').value || undefined,
          client_ip: document.getElementById('q_client_ip').value || undefined,
          method: document.getElementById('q_method').value || undefined,
          status_code: document.getElementById('q_status').value ? Number(document.getElementById('q_status').value) : undefined,
          min_response_time: document.getElementById('q_min_rt').value ? Number(document.getElementById('q_min_rt').value) : undefined,
        }
      };
      const data = await fetchJSON('/admin/monitor/requests/search', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const list = (data.requests || []);
      const tbody = document.querySelector('#tbl_requests tbody');
      tbody.innerHTML = '';
      list.forEach(x => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${x.timestamp || ''}</td><td>${x.request_id || ''}</td><td>${x.method || ''}</td><td>${x.endpoint || ''}</td><td>${x.response_status || ''}</td><td>${x.process_time || ''}</td><td>${x.client_ip || ''}</td>`;
        tbody.appendChild(tr);
      });
      const pg = data.pagination || {}; 
      document.getElementById('pg_info').textContent = `第 ${pg.current_page||1}/${pg.total_pages||1} 页，共 ${pg.total_count||0} 条`;
    }

    async function refreshAll() {
      await Promise.all([
        loadRealtime(),
        loadAlerts(),
        loadTrend(),
        searchRequests(1, 20)
      ]);
    }

    let timer = null;
    function applyAutoRefresh() {
      if (timer) { clearInterval(timer); timer = null; }
      const sec = Number(document.getElementById('autoRefresh').value || 0);
      if (sec > 0) timer = setInterval(refreshAll, sec * 1000);
    }

    document.getElementById('refreshBtn').addEventListener('click', refreshAll);
    document.getElementById('autoRefresh').addEventListener('change', () => { applyAutoRefresh(); refreshAll(); });
    document.getElementById('days').addEventListener('change', loadTrend);
    document.getElementById('btn_search').addEventListener('click', () => searchRequests(1, 20));

    // 首次加载
    refreshAll().catch(console.error);
    applyAutoRefresh();
  </script>
</body>
</html>
    """)


@monitor_bp.route('/dashboard', methods=['GET'])
@monitor_request
def dashboard():
    """监控面板首页"""
    try:
        # 获取实时指标
        realtime_data = get_realtime_metrics()
        
        # 获取告警信息
        alerts = get_performance_alerts()
        
        return jsonify({
            'code': 0,
            'status': 'success',
            'message': 'success',
            'data': {
                'realtime_metrics': realtime_data,
                'alerts': alerts,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to get dashboard data',
            'error': str(e)
        }), 500


@monitor_bp.route('/metrics/realtime', methods=['GET'])
@monitor_request
def realtime_metrics():
    """获取实时监控指标"""
    try:
        data = get_realtime_metrics()
        return jsonify({
            'code': 0,
            'status': 'success',
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to get realtime metrics',
            'error': str(e)
        }), 500


@monitor_bp.route('/traffic/trend', methods=['GET'])
@monitor_request
def traffic_trend():
    """获取流量趋势分析"""
    try:
        days = request.args.get('days', 7, type=int)
        if days < 1 or days > 90:
            days = 7
            
        data = get_traffic_trend(days)
        return jsonify({
            'code': 0,
            'status': 'success',
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to get traffic trend',
            'error': str(e)
        }), 500


@monitor_bp.route('/endpoints/analysis', methods=['GET'])
@monitor_request
def endpoint_analysis():
    """获取端点性能分析"""
    try:
        days = request.args.get('days', 7, type=int)
        if days < 1 or days > 90:
            days = 7
            
        data = get_endpoint_analysis(days)
        return jsonify({
            'code': 0,
            'status': 'success',
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to get endpoint analysis',
            'error': str(e)
        }), 500


@monitor_bp.route('/users/behavior', methods=['GET'])
@monitor_request
def user_behavior():
    """获取用户行为分析"""
    try:
        days = request.args.get('days', 7, type=int)
        if days < 1 or days > 90:
            days = 7
            
        data = get_user_behavior_analysis(days)
        return jsonify({
            'code': 0,
            'status': 'success',
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to get user behavior analysis',
            'error': str(e)
        }), 500


@monitor_bp.route('/alerts', methods=['GET'])
@monitor_request
def alerts():
    """获取性能告警信息"""
    try:
        data = get_performance_alerts()
        return jsonify({
            'code': 0,
            'status': 'success',
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to get alerts',
            'error': str(e)
        }), 500


@monitor_bp.route('/reports/daily', methods=['GET'])
@monitor_request
def daily_report():
    """获取日报告"""
    try:
        date_str = request.args.get('date')
        target_date = None
        
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'code': 400,
                    'status': 'error',
                    'message': 'Invalid date format. Use YYYY-MM-DD'
                }), 400
        
        data = generate_daily_report(target_date)
        return jsonify({
            'code': 0,
            'status': 'success',
            'message': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to generate daily report',
            'error': str(e)
        }), 500


@monitor_bp.route('/requests/search', methods=['POST'])
@monitor_request
def search_requests():
    """搜索请求记录"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'status': 'error',
                'message': 'Missing request data'
            }), 400
        
        # 搜索参数
        page = data.get('page', 1)
        page_size = min(data.get('page_size', 50), 200)  # 限制页面大小
        
        filters = data.get('filters', {})
        start_time = filters.get('start_time')
        end_time = filters.get('end_time')
        endpoint = filters.get('endpoint')
        client_ip = filters.get('client_ip')
        method = filters.get('method')
        status_code = filters.get('status_code')
        min_response_time = filters.get('min_response_time')
        
        connection = route_monitor.pool.connection()
        try:
            with connection.cursor() as cursor:
                # 构建查询条件
                where_conditions = ["1=1"]
                params = []
                
                if start_time:
                    where_conditions.append("timestamp >= %s")
                    params.append(start_time)
                
                if end_time:
                    where_conditions.append("timestamp <= %s")
                    params.append(end_time)
                
                if endpoint:
                    where_conditions.append("endpoint LIKE %s")
                    params.append(f"%{endpoint}%")
                
                if client_ip:
                    where_conditions.append("client_ip = %s")
                    params.append(client_ip)
                
                if method:
                    where_conditions.append("method = %s")
                    params.append(method)
                
                if status_code:
                    where_conditions.append("response_status = %s")
                    params.append(status_code)
                
                if min_response_time:
                    where_conditions.append("process_time >= %s")
                    params.append(min_response_time)
                
                where_clause = " AND ".join(where_conditions)
                
                # 获取总数
                count_sql = f"SELECT COUNT(*) as total FROM api_request_logs WHERE {where_clause}"
                cursor.execute(count_sql, params)
                total_count = cursor.fetchone()['total']
                
                # 分页查询
                offset = (page - 1) * page_size
                search_sql = f"""
                    SELECT 
                        request_id, timestamp, method, endpoint, client_ip, real_ip,
                        response_status, process_time, user_agent, referer,
                        is_bot, is_mobile, browser_name, os_name
                    FROM api_request_logs 
                    WHERE {where_clause}
                    ORDER BY timestamp DESC
                    LIMIT %s OFFSET %s
                """
                
                cursor.execute(search_sql, params + [page_size, offset])
                results = cursor.fetchall()
                
                return jsonify({
                    'code': 0,
                    'status': 'success',
                    'message': 'success',
                    'data': {
                        'requests': results,
                        'pagination': {
                            'current_page': page,
                            'page_size': page_size,
                            'total_count': total_count,
                            'total_pages': (total_count + page_size - 1) // page_size
                        }
                    }
                })
        finally:
            connection.close()
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to search requests',
            'error': str(e)
        }), 500


@monitor_bp.route('/requests/<request_id>', methods=['GET'])
@monitor_request
def get_request_detail(request_id):
    """获取请求详细信息"""
    try:
        connection = route_monitor.pool.connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM api_request_logs WHERE request_id = %s
                """, (request_id,))
                
                request_detail = cursor.fetchone()
                
                if not request_detail:
                    return jsonify({
                        'code': 404,
                        'status': 'error',
                        'message': 'Request not found'
                    }), 404
                
                # 安全地转换JSON字段
                json_fields = ['request_headers', 'request_params', 'request_body', 'device_info', 'business_data', 'tags']
                for field in json_fields:
                    if request_detail.get(field):
                        try:
                            # 使用json.loads替代eval，更安全
                            if isinstance(request_detail[field], str):
                                request_detail[field] = json.loads(request_detail[field])
                        except (json.JSONDecodeError, TypeError):
                            # 如果解析失败，保持原值
                            pass
                
                return jsonify({
                    'code': 0,
                    'status': 'success',
                    'message': 'success',
                    'data': request_detail
                })
        finally:
            connection.close()
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to get request detail',
            'error': str(e)
        }), 500


@monitor_bp.route('/statistics/summary', methods=['GET'])
@monitor_request
def statistics_summary():
    """获取统计摘要"""
    try:
        days = request.args.get('days', 7, type=int)
        if days < 1 or days > 90:
            days = 7
        
        connection = route_monitor.pool.connection()
        try:
            with connection.cursor() as cursor:
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=days)
                
                # 综合统计
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_requests,
                        COUNT(DISTINCT client_ip) as unique_ips,
                        COUNT(DISTINCT endpoint) as unique_endpoints,
                        COUNT(DISTINCT DATE(timestamp)) as active_days,
                        AVG(process_time) as avg_response_time,
                        MAX(process_time) as max_response_time,
                        SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) as error_count,
                        SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) / COUNT(*) * 100 as error_rate,
                        SUM(CASE WHEN is_bot = 1 THEN 1 ELSE 0 END) as bot_requests,
                        SUM(CASE WHEN is_mobile = 1 THEN 1 ELSE 0 END) as mobile_requests,
                        SUM(request_size) as total_request_size,
                        SUM(response_size) as total_response_size
                    FROM api_request_logs 
                    WHERE DATE(timestamp) BETWEEN %s AND %s
                """, (start_date, end_date))
                
                summary = cursor.fetchone()
                
                # 每日趋势
                cursor.execute("""
                    SELECT 
                        DATE(timestamp) as date,
                        COUNT(*) as requests,
                        COUNT(DISTINCT client_ip) as unique_ips,
                        AVG(process_time) as avg_response_time,
                        SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) as errors
                    FROM api_request_logs 
                    WHERE DATE(timestamp) BETWEEN %s AND %s
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                """, (start_date, end_date))
                
                daily_trend = cursor.fetchall()
                
                return jsonify({
                    'code': 0,
                    'status': 'success',
                    'message': 'success',
                    'data': {
                        'period': f'{start_date} to {end_date}',
                        'summary': summary,
                        'daily_trend': daily_trend
                    }
                })
        finally:
            connection.close()
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to get statistics summary',
            'error': str(e)
        }), 500


@monitor_bp.route('/data/cleanup', methods=['POST'])
@monitor_request  
def data_cleanup():
    """数据清理功能"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'code': 400,
                'status': 'error',
                'message': 'Missing request data'
            }), 400
        
        cleanup_type = data.get('type', 'old_logs')
        days_to_keep = data.get('days_to_keep', 30)
        
        if days_to_keep < 7:  # 至少保留7天
            return jsonify({
                'code': 400,
                'status': 'error',
                'message': 'Must keep at least 7 days of data'
            }), 400
        
        connection = route_monitor.pool.connection()
        try:
            with connection.cursor() as cursor:
                cleanup_date = datetime.now() - timedelta(days=days_to_keep)
                
                if cleanup_type == 'old_logs':
                    # 清理旧的请求日志
                    cursor.execute("""
                        DELETE FROM api_request_logs 
                        WHERE timestamp < %s
                    """, (cleanup_date,))
                    
                    deleted_count = cursor.rowcount
                    
                elif cleanup_type == 'old_statistics':
                    # 清理旧的统计数据
                    cursor.execute("""
                        DELETE FROM api_access_statistics 
                        WHERE date < %s
                    """, (cleanup_date.date(),))
                    
                    deleted_count = cursor.rowcount
                    
                elif cleanup_type == 'old_ip_stats':
                    # 清理旧的IP统计
                    cursor.execute("""
                        DELETE FROM ip_access_statistics 
                        WHERE date < %s
                    """, (cleanup_date.date(),))
                    
                    deleted_count = cursor.rowcount
                    
                else:
                    return jsonify({
                        'code': 400,
                        'status': 'error',
                        'message': 'Invalid cleanup type'
                    }), 400
                
            connection.commit()
            
            return jsonify({
                'code': 0,
                'status': 'success',
                'message': 'Data cleanup completed',
                'data': {
                    'cleanup_type': cleanup_type,
                    'deleted_count': deleted_count,
                    'cleanup_date': cleanup_date.isoformat()
                }
            })
        finally:
            connection.close()
         
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Failed to cleanup data',
            'error': str(e)
        }), 500


@monitor_bp.route('/health', methods=['GET'])
def health_check():
    """监控系统健康检查"""
    try:
        # 检查数据库连接
        connection = route_monitor.pool.connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_status = "OK"
        
            # 检查最近的数据
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as recent_count 
                    FROM api_request_logs 
                    WHERE timestamp >= %s
                """, (datetime.now() - timedelta(hours=1),))
                
                recent_requests = cursor.fetchone()['recent_count']
        finally:
            connection.close()
        
        return jsonify({
            'code': 0,
            'status': 'success',
            'message': 'Monitor system is healthy',
            'data': {
                'database_status': db_status,
                'recent_requests_count': recent_requests,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': 'Monitor system health check failed',
            'error': str(e)
        }), 500


# 导出蓝图注册函数
def register_routes(app):
    """注册监控路由到Flask应用"""
    app.register_blueprint(monitor_bp) 