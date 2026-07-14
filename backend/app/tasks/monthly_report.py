from app.celery_worker import celery_app

@celery_app.task(name='app.tasks.monthly_report.send_monthly_report', bind=True)

def send_monthly_report(self):

    from app import create_app

    app = create_app()

    with app.app_context():

        from datetime import datetime

        from calendar import monthrange

        from app.models import PlacementDrive, Application, User, StudentProfile

        from flask_mail import Message

        from app.extensions import mail

        now = datetime.utcnow()

        if now.month == 1:

            report_month, report_year = 12, now.year - 1

        else:

            report_month, report_year = now.month - 1, now.year

        month_start = datetime(report_year, report_month, 1)

        last_day    = monthrange(report_year, report_month)[1]

        month_end   = datetime(report_year, report_month, last_day, 23, 59, 59)

        month_name  = month_start.strftime('%B %Y')

        drives_this_month = PlacementDrive.query.filter(

            PlacementDrive.created_at >= month_start,

            PlacementDrive.created_at <= month_end

        ).all()

        drives_count = len(drives_this_month)

        apps = Application.query.filter(

            Application.applied_at >= month_start,

            Application.applied_at <= month_end

        ).all()

        total       = len(apps)

        selected    = sum(1 for a in apps if a.status == 'selected')

        shortlisted = sum(1 for a in apps if a.status == 'shortlisted')

        rejected    = sum(1 for a in apps if a.status == 'rejected')

        pending     = sum(1 for a in apps if a.status not in ('selected', 'shortlisted', 'rejected'))

        drive_stats = {}

        for app_rec in apps:

            d_id = app_rec.drive_id

            if d_id not in drive_stats:

                drive_stats[d_id] = {

                    'name': app_rec.drive.drive_name,

                    'company': app_rec.drive.company.company_name if app_rec.drive.company else '—',

                    'applicants': 0,

                    'selected': 0

                }

            drive_stats[d_id]['applicants'] += 1

            if app_rec.status == 'selected':

                drive_stats[d_id]['selected'] += 1

        sorted_drives = sorted(drive_stats.values(), key=lambda x: x['applicants'], reverse=True)[:5]

        drive_rows = ''

        for d in sorted_drives:

            drive_rows += f"""
            <tr>
              <td>{d['name']}</td>
              <td>{d['company']}</td>
              <td style="text-align:center">{d['applicants']}</td>
              <td style="text-align:center; color:#2e7d32; font-weight:bold;">{d['selected']}</td>
            </tr>
            """

        if not drive_rows:

            drive_rows = '<tr><td colspan="4" style="text-align:center; color:#777;">No drive activity recorded.</td></tr>'

        html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body {{  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background-color: #f4f6f9; padding: 20px; }} 
        .card {{  background: white; border-radius: 8px; padding: 32px; max-width: 650px; margin: auto; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }} 
        .header {{  border-bottom: 2px solid #eaeaea; padding-bottom: 16px; margin-bottom: 24px; }} 
        .header h2 {{  margin: 0; color: #2c3e50; font-size: 24px; }} 
        .header p {{  margin: 4px 0 0; color: #7f8c8d; font-size: 14px; }} 
        .stat-grid {{  display: flex; gap: 16px; margin-bottom: 24px; }} 
        .stat-box {{  flex: 1; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 16px; text-align: center; }} 
        .stat-val {{  font-size: 28px; font-weight: bold; color: #6c63ff; margin-bottom: 4px; }} 
        .stat-lbl {{  font-size: 12px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 0.5px; }} 
        table {{  width: 100%; border-collapse: collapse; margin-top: 16px; }} 
        th {{  background: #f8f9fa; color: #333; text-align: left; padding: 10px; font-size: 14px; border-bottom: 2px solid #dee2e6; }} 
        td {{  padding: 10px; border-bottom: 1px solid #eee; font-size: 14px; }} 
        .footer {{  text-align: center; margin-top: 30px; font-size: 12px; color: #aaa; }} 
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <h2>📊 Monthly Placement Activity Report</h2>
          <p>For Period: {month_name}</p>
        </div>

        <div class="stat-grid">
          <div class="stat-box">
            <div class="stat-val">{drives_count}</div>
            <div class="stat-lbl">Drives Conducted</div>
          </div>
          <div class="stat-box">
            <div class="stat-val">{total}</div>
            <div class="stat-lbl">Total Applicants</div>
          </div>
          <div class="stat-box">
            <div class="stat-val" style="color: #2e7d32;">{selected}</div>
            <div class="stat-lbl">Students Selected</div>
          </div>
        </div>

        <h3>Application Status Breakdown</h3>
        <table>
          <tr><th>Status</th><th>Count</th><th>Percentage</th></tr>
          <tr><td>✅ Selected</td><td>{selected}</td><td>{round(selected/total*100,1) if total else 0}%</td></tr>
          <tr><td>📋 Shortlisted</td><td>{shortlisted}</td><td>{round(shortlisted/total*100,1) if total else 0}%</td></tr>
          <tr><td>❌ Rejected</td><td>{rejected}</td><td>{round(rejected/total*100,1) if total else 0}%</td></tr>
          <tr><td>⏳ Pending</td><td>{pending}</td><td>{round(pending/total*100,1) if total else 0}%</td></tr>
        </table>

        <!-- Top drives -->
        <h3 style="margin-top:28px">Top Drives by Applicants</h3>
        <table>
          <tr><th>Drive</th><th>Company</th><th style="text-align:center">Applicants</th><th style="text-align:center">Selected</th></tr>
          {drive_rows}
        </table>
      </div>

      <div class="footer">
        This report was automatically generated by PlaceMe &nbsp;·&nbsp;
        Report period: {month_start.strftime('%d %b')} – {month_end.strftime('%d %b %Y')}
      </div>
    </body>
    </html>
        """.strip()

        admin = User.query.filter_by(role='admin').first()

        if not admin:

            return {'status': 'error', 'message': 'No admin found.'}

        try:

            msg = Message(

                subject=f'📊 [PlaceMe] Monthly Report — {month_name}',

                recipients=[admin.email],

                html=html_body

            )

            mail.send(msg)

            print(f'[Monthly Report] Sent to {admin.email}')

            return {'status': 'success', 'message': f'Report sent to {admin.email}', 'month': month_name}

        except Exception as e:

            print(f'[Monthly Report] Failed: {e}')

            return {'status': 'error', 'message': str(e)}
