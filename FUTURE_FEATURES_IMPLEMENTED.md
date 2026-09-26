# EMS Future Features Implemented

The following requested features are integrated into the Flask Event Management System:

1. **Live Event Tracking** – event status API (Upcoming/Live/Completed), automatic refresh, and venue map link.
2. **QR Code Check-In** – admin camera scanner using `html5-qrcode` plus manual registration-ID check-in; attendance is stored in the database.
3. **Email & SMS Notifications** – SMTP email support and optional Twilio SMS support with notification logs.
4. **Advanced Analytics Dashboard** – registrations, attendance, waitlist, feedback rating, and attendance percentage by event.
5. **Feedback & Rating System** – registered users can submit/update a 1–5 rating and comment.
6. **Calendar Integration (.ics)** – each event has a downloadable RFC-style `.ics` calendar file.
7. **Cloud Database & Storage Ready** – production already supports MySQL via `DATABASE_URL`; S3-compatible storage upload helper is included and activated through environment variables.
8. **Event Waitlist System** – full events accept waitlist entries; cancellations automatically promote the oldest waiting user and generate a QR ticket.
9. **Automated Attendance Reports + CSV Export** – check-in data is stored and downloadable as `attendance_report.csv` from the admin analytics page.

## Configuration

Copy `.env.example` to `.env` and configure SMTP/Twilio/cloud values when those services are available. The application remains usable locally with SQLite even when optional external services are not configured.
