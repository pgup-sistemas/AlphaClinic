"""
Blueprint para Relatórios de Compliance
Interface web para geração e visualização de relatórios de compliance
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from compliance_service import ComplianceReportService
from audit_service import AuditService
from datetime import datetime, timedelta
import json

compliance_bp = Blueprint('compliance', __name__)

@compliance_bp.route('/')
@login_required
def index():
    """Dashboard de compliance"""
    # Verificar permissões (apenas admin, manager, auditor)
    if current_user.role.value not in ['admin', 'manager', 'auditor']:
        flash('Sem permissão para acessar relatórios de compliance.', 'error')
        return redirect(url_for('main.dashboard'))

    # Gerar relatório overview
    report = ComplianceReportService.generate_compliance_overview()

    return render_template('compliance/index.html', report=report)

@compliance_bp.route('/reports/overview')
@login_required
def overview_report():
    """Relatório geral de compliance"""
    if current_user.role.value not in ['admin', 'manager', 'auditor']:
        flash('Sem permissão para acessar relatórios.', 'error')
        return redirect(url_for('main.dashboard'))

    # Parâmetros de data
    days = int(request.args.get('days', 30))
    start_date = datetime.utcnow() - timedelta(days=days)
    end_date = datetime.utcnow()

    report = ComplianceReportService.generate_compliance_overview(start_date, end_date)

    return render_template('compliance/overview.html', report=report, days=days)

@compliance_bp.route('/reports/gdpr')
@login_required
def gdpr_report():
    """Relatório de compliance LGPD"""
    if current_user.role.value not in ['admin', 'manager', 'auditor']:
        flash('Sem permissão para acessar relatórios LGPD.', 'error')
        return redirect(url_for('main.dashboard'))

    report = ComplianceReportService.generate_gdpr_compliance_report()

    return render_template('compliance/gdpr.html', report=report)

@compliance_bp.route('/reports/iso9001')
@login_required
def iso9001_report():
    """Relatório de compliance ISO 9001"""
    if current_user.role.value not in ['admin', 'manager', 'auditor']:
        flash('Sem permissão para acessar relatórios ISO 9001.', 'error')
        return redirect(url_for('main.dashboard'))

    report = ComplianceReportService.generate_iso9001_compliance_report()

    return render_template('compliance/iso9001.html', report=report)

@compliance_bp.route('/audit-trail')
@login_required
def audit_trail():
    """Visualização da trilha de auditoria"""
    if current_user.role.value not in ['admin', 'auditor']:
        flash('Sem permissão para acessar trilha de auditoria.', 'error')
        return redirect(url_for('main.dashboard'))

    # Parâmetros de filtro
    entity_type = request.args.get('entity_type')
    user_id = request.args.get('user_id')
    limit = min(int(request.args.get('limit', 100)), 500)
    offset = int(request.args.get('offset', 0))

    # Obter trilha de auditoria
    audit_data = AuditService.get_audit_trail(
        entity_type=entity_type,
        user_id=user_id,
        limit=limit,
        offset=offset
    )

    return render_template('compliance/audit_trail.html',
                         audit_data=audit_data,
                         entity_type=entity_type,
                         user_id=user_id,
                         limit=limit,
                         offset=offset)

@compliance_bp.route('/api/reports/overview')
@login_required
def api_overview_report():
    """API para relatório overview"""
    if current_user.role.value not in ['admin', 'manager', 'auditor']:
        return jsonify({'error': 'Unauthorized'}), 403

    days = int(request.args.get('days', 30))
    start_date = datetime.utcnow() - timedelta(days=days)
    end_date = datetime.utcnow()

    report = ComplianceReportService.generate_compliance_overview(start_date, end_date)

    return jsonify(report)

@compliance_bp.route('/api/audit-trail')
@login_required
def api_audit_trail():
    """API para trilha de auditoria"""
    if current_user.role.value not in ['admin', 'auditor']:
        return jsonify({'error': 'Unauthorized'}), 403

    entity_type = request.args.get('entity_type')
    user_id = request.args.get('user_id')
    limit = min(int(request.args.get('limit', 100)), 500)
    offset = int(request.args.get('offset', 0))

    audit_data = AuditService.get_audit_trail(
        entity_type=entity_type,
        user_id=user_id,
        limit=limit,
        offset=offset
    )

    return jsonify(audit_data)

@compliance_bp.route('/api/verify-integrity')
@login_required
def verify_integrity():
    """Verificar integridade da trilha de auditoria"""
    if current_user.role.value not in ['admin', 'auditor']:
        return jsonify({'error': 'Unauthorized'}), 403

    integrity_result = AuditService.verify_audit_integrity()

    # Log da verificação
    AuditService.log_operation(
        entity_type='compliance',
        entity_id=0,
        operation='verify_audit_integrity',
        operation_details={'result': integrity_result[0], 'message': integrity_result[1]},
        compliance_level='critical'
    )

    return jsonify({
        'integrity_verified': integrity_result[0],
        'message': integrity_result[1],
        'verified_at': datetime.utcnow().isoformat()
    })

@compliance_bp.route('/export/<report_type>')
@login_required
def export_report(report_type):
    """Exportar relatório"""
    if current_user.role.value not in ['admin', 'manager', 'auditor']:
        flash('Sem permissão para exportar relatórios.', 'error')
        return redirect(url_for('compliance.index'))

    format_type = request.args.get('format', 'json')

    try:
        if report_type == 'overview':
            report = ComplianceReportService.generate_compliance_overview()
        elif report_type == 'gdpr':
            report = ComplianceReportService.generate_gdpr_compliance_report()
        elif report_type == 'iso9001':
            report = ComplianceReportService.generate_iso9001_compliance_report()
        else:
            flash('Tipo de relatório inválido.', 'error')
            return redirect(url_for('compliance.index'))

        # Exportar
        exported_data = ComplianceReportService.export_report(report, format_type)

        # Log da exportação
        AuditService.log_operation(
            entity_type='compliance',
            entity_id=0,
            operation='export_report',
            operation_details={'report_type': report_type, 'format': format_type},
            compliance_level='standard'
        )

        # Para JSON, retornar como arquivo para download
        from flask import Response
        response = Response(
            exported_data,
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename=compliance_{report_type}_{datetime.utcnow().strftime("%Y%m%d")}.json'}
        )
        return response

    except Exception as e:
        current_app.logger.error(f"Error exporting report: {str(e)}")
        flash('Erro ao exportar relatório.', 'error')
        return redirect(url_for('compliance.index'))