from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from analytics_service import analytics_service
from models import DashboardWidget, DashboardLayout, db
from datetime import datetime
import json
import io

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/')
@login_required
def analytics_dashboard():
    """Dashboard de analytics e BI"""
    # Obter dados do dashboard
    dashboard_data = analytics_service.get_dashboard_data(current_user.id)

    return render_template('analytics/dashboard.html', data=dashboard_data)

@analytics_bp.route('/api/metrics')
@login_required
def get_metrics():
    """API para obter métricas em tempo real"""
    try:
        # Garantir que temos acesso ao banco de dados
        if not db.session:
            return jsonify({'error': 'Database connection not available'}), 500

        metrics = analytics_service.get_dashboard_data(current_user.id)
        return jsonify(metrics)
    except Exception as e:
        print(f"Erro na API de métricas: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/charts/<chart_type>')
@login_required
def get_chart_data(chart_type):
    """API para obter dados de gráficos"""
    try:
        period = request.args.get('period', '30d')
        category = request.args.get('category')

        chart_data = analytics_service.get_chart_data(chart_type, period, category)
        return jsonify(chart_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/export/<data_type>')
@login_required
def export_data(data_type):
    """Exportar dados em formato específico"""
    try:
        export_format = request.args.get('format', 'excel')
        filters = dict(request.args)

        # Remover parâmetros não relacionados a filtros
        filters.pop('format', None)

        export_result = analytics_service.export_data(export_format, data_type, filters)

        if export_result:
            # Criar arquivo temporário
            file_data = io.BytesIO(export_result['data'])

            return send_file(
                file_data,
                as_attachment=True,
                download_name=export_result['filename'],
                mimetype=export_result['mimetype']
            )
        else:
            return jsonify({'error': 'Erro na exportação'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/widgets')
@login_required
def manage_widgets():
    """Gerenciar widgets do dashboard"""
    widgets = DashboardWidget.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).order_by(DashboardWidget.position_y, DashboardWidget.position_x).all()

    return render_template('analytics/widgets.html', widgets=widgets)

@analytics_bp.route('/widgets/create', methods=['GET', 'POST'])
@login_required
def create_widget():
    """Criar novo widget personalizado"""
    if request.method == 'POST':
        try:
            widget = DashboardWidget(
                user_id=current_user.id,
                name=request.form['name'],
                widget_type=request.form['widget_type'],
                title=request.form['title'],
                config=json.loads(request.form.get('config', '{}')),
                position_x=int(request.form.get('position_x', 0)),
                position_y=int(request.form.get('position_y', 0)),
                width=int(request.form.get('width', 1)),
                height=int(request.form.get('height', 1)),
                icon=request.form.get('icon'),
                color_scheme=request.form.get('color_scheme', 'blue')
            )

            db.session.add(widget)
            db.session.commit()

            return jsonify({'success': True, 'widget_id': widget.id})

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    return render_template('analytics/create_widget.html')

@analytics_bp.route('/widgets/<int:widget_id>/update', methods=['POST'])
@login_required
def update_widget(widget_id):
    """Atualizar widget"""
    widget = DashboardWidget.query.filter_by(
        id=widget_id,
        user_id=current_user.id
    ).first()

    if not widget:
        return jsonify({'success': False, 'error': 'Widget não encontrado'}), 404

    try:
        widget.name = request.form['name']
        widget.title = request.form['title']
        widget.widget_type = request.form['widget_type']
        widget.config = json.loads(request.form.get('config', '{}'))
        widget.position_x = int(request.form.get('position_x', widget.position_x))
        widget.position_y = int(request.form.get('position_y', widget.position_y))
        widget.width = int(request.form.get('width', widget.width))
        widget.height = int(request.form.get('height', widget.height))
        widget.icon = request.form.get('icon')
        widget.color_scheme = request.form.get('color_scheme', widget.color_scheme)

        db.session.commit()
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/widgets/<int:widget_id>/delete', methods=['POST'])
@login_required
def delete_widget(widget_id):
    """Excluir widget"""
    widget = DashboardWidget.query.filter_by(
        id=widget_id,
        user_id=current_user.id
    ).first()

    if not widget:
        return jsonify({'success': False, 'error': 'Widget não encontrado'}), 404

    try:
        widget.is_active = False
        db.session.commit()
        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/layouts')
@login_required
def manage_layouts():
    """Gerenciar layouts do dashboard"""
    layouts = DashboardLayout.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()

    return render_template('analytics/layouts.html', layouts=layouts)

@analytics_bp.route('/layouts/save', methods=['POST'])
@login_required
def save_layout():
    """Salvar layout personalizado"""
    try:
        layout_data = json.loads(request.form['layout_data'])
        layout_name = request.form.get('layout_name', 'custom')

        # Verificar se layout já existe
        layout = DashboardLayout.query.filter_by(
            user_id=current_user.id,
            layout_name=layout_name
        ).first()

        if not layout:
            layout = DashboardLayout(
                user_id=current_user.id,
                layout_name=layout_name
            )

        layout.layout_data = layout_data
        layout.columns = int(request.form.get('columns', 3))
        layout.auto_refresh = request.form.get('auto_refresh') == 'true'
        layout.refresh_interval = int(request.form.get('refresh_interval', 300))

        db.session.add(layout)
        db.session.commit()

        return jsonify({'success': True, 'layout_id': layout.id})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/predictions/nc-risk')
@login_required
def get_nc_risk_prediction():
    """API para obter predição de risco de NCs"""
    try:
        prediction = analytics_service.predict_nc_risk(current_user.id)
        return jsonify(prediction)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/offline-documents')
@login_required
def offline_documents():
    """Gerenciar documentos offline"""
    from models import OfflineDocument

    offline_docs = OfflineDocument.query.filter_by(
        user_id=current_user.id,
        is_available=True
    ).order_by(OfflineDocument.downloaded_at.desc()).all()

    return render_template('analytics/offline_documents.html', offline_docs=offline_docs)

@analytics_bp.route('/offline-documents/<int:document_id>/download', methods=['POST'])
@login_required
def download_offline_document(document_id):
    """Baixar documento para uso offline"""
    from models import Document, OfflineDocument

    document = Document.query.get_or_404(document_id)

    # Verificar se já existe
    existing = OfflineDocument.query.filter_by(
        document_id=document_id,
        user_id=current_user.id,
        is_available=True
    ).first()

    if existing:
        return jsonify({'success': False, 'message': 'Documento já disponível offline'})

    try:
        # Criar cópia offline
        offline_doc = OfflineDocument(
            document_id=document_id,
            user_id=current_user.id,
            content_snapshot=document.content,
            version_snapshot=document.version,
            expires_at=datetime.utcnow() + timedelta(days=30)  # Expira em 30 dias
        )

        db.session.add(offline_doc)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Documento baixado para uso offline'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/push-notifications')
@login_required
def push_notifications():
    """Gerenciar notificações push"""
    from models import PushNotification

    notifications = PushNotification.query.filter_by(
        user_id=current_user.id
    ).order_by(PushNotification.created_at.desc()).limit(50).all()

    return render_template('analytics/push_notifications.html', notifications=notifications)

@analytics_bp.route('/api/push-notifications/test', methods=['POST'])
@login_required
def test_push_notification():
    """Enviar notificação push de teste"""
    try:
        from models import PushNotification

        notification = PushNotification(
            user_id=current_user.id,
            title='Notificação de Teste',
            message='Esta é uma notificação push de teste do Alphaclin QMS',
            category='system',
            priority='normal'
        )

        db.session.add(notification)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Notificação de teste enviada'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/collect-metrics', methods=['POST'])
@login_required
def collect_metrics():
    """Endpoint para coletar métricas manualmente"""
    try:
        count = analytics_service.collect_daily_metrics()
        return jsonify({
            'success': True,
            'message': f'{count} métricas coletadas com sucesso'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500