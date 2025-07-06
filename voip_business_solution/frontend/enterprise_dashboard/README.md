# VoIP Enterprise Dashboard (Enhanced)

This directory contains the frontend React application for administrators and customer service representatives of the VoIP Business Solution.

## Features (Conceptual)

Based on the system architecture, this dashboard should provide interfaces for:

*   **Admin Authentication:** Secure login for authorized personnel.
*   **Dashboard Overview:** Key system metrics, alerts, and operational status.
*   **User Management:**
    *   View and search for users.
    *   View user details (profile, subscriptions, activity).
    *   Manually activate/deactivate users.
    *   Reset user passwords (with security protocols).
    *   Manage user roles and permissions (if applicable).
*   **KYC Management & Review:**
    *   View KYC submission queue.
    *   Review submitted documents and selfie images.
    *   Compare OCR data with document images.
    *   Check biometric verification results and risk scores.
    *   Approve or reject KYC applications.
    *   Add notes to KYC records.
    *   Manage high-risk accounts flagged for manual review.
*   **Subscription Management (Oversight):**
    *   View all user subscriptions.
    *   Filter and search subscriptions (by plan, user, status).
    *   Manually adjust subscriptions (e.g., change plan, extend trial, apply credits - with audit trails).
    *   View detailed usage for specific subscriptions.
*   **Billing and Payments (Oversight):**
    *   View transaction history.
    *   Search for payments.
    *   Manage refunds and disputes (process or flag for finance).
    *   Oversee invoicing processes.
*   **DID Number Management (Admin):**
    *   View inventory of DID numbers.
    *   Assign DIDs to users or services.
    *   Manage DID provider integrations (view status, provision new numbers if API allows).
*   **Call Detail Records (CDR) & SMS Records Access:**
    *   Search and view call logs for troubleshooting or monitoring.
    *   Search and view SMS logs.
*   **System Monitoring Interface:**
    *   Display real-time metrics (e.g., from Prometheus/Grafana - can be embedded or linked).
    *   View call volumes, active users, server status.
    *   Error rates and system health indicators.
*   **Analytics & Reporting:**
    *   Generate reports on user acquisition, revenue, call traffic, KYC processing times, etc.
    *   Visualize data with charts and graphs.
*   **Configuration Management (Limited):**
    *   Manage certain system settings if exposed via API (e.g., promotional messages, rate adjustments within limits).
*   **Audit Logs:**
    *   View logs of administrative actions taken through the dashboard.

## Tech Stack (Assumed)

Similar to the User Application:

*   **React:** For building the user interface.
*   **State Management:** Redux, Zustand, or React Context API.
*   **Routing:** React Router.
*   **API Communication:** Axios or Fetch API.
*   **Styling:** CSS Modules, Styled Components, Tailwind CSS, or a UI library (e.g., Material-UI, Ant Design - often chosen for admin dashboards for pre-built components).
*   **Data Visualization:** Libraries like Chart.js, Recharts, Nivo for analytics.

## Setup and Build (Placeholder Commands)

1.  **Install Dependencies:**
    ```bash
    npm install
    # or
    yarn install
    ```

2.  **Run Development Server:**
    ```bash
    npm start
    # or
    yarn start
    ```
    Proxy API requests to the backend as needed.

3.  **Build for Production:**
    ```bash
    npm run build
    # or
    yarn build
    ```
    Output will be in `build/` or `dist/`. The Nginx configuration (`nginx.conf`) expects it in `/opt/voip-enterprise-dashboard-enhanced/dist`.

## Nginx Configuration

An example Nginx configuration (`nginx.conf`) is provided. Key features:
*   Serves the static React application.
*   Client-side routing support.
*   API proxy (`/api/`) to the backend.
*   SSL/TLS.
*   Enhanced security headers (X-Frame-Options: DENY, stricter CSP).
*   Basic Authentication for an added security layer.
*   Optional IP whitelisting.

## Further Development

This is a foundational setup. The actual implementation requires:
*   Building all React components for the features listed.
*   Secure API integration, especially for administrative actions.
*   Role-based access control within the frontend to show/hide features based on admin roles.
*   Robust data tables, filtering, and search functionalities.
*   Comprehensive error handling and logging.
*   Testing (unit, integration, E2E).
