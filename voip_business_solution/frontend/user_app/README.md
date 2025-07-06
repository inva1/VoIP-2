# VoIP User Application (Enhanced)

This directory contains the frontend React application for users of the VoIP Business Solution.

## Features (Conceptual)

Based on the system architecture, this application should provide interfaces for:

*   **User Authentication:** Login, registration, password reset.
*   **Dashboard:** Overview of services, recent activity.
*   **Subscription Management:**
    *   View available subscription plans (for calling to US, UK, Nigeria, etc., based on user type).
    *   Subscribe to new plans.
    *   View current active subscriptions.
    *   Manage auto-renewal.
    *   View usage (minutes, messages).
*   **KYC Verification:**
    *   Submit identity documents (passport, ID card, driver's license).
    *   Upload document images (front, back).
    *   Capture and submit a selfie for biometric verification.
    *   View KYC status (pending, verified, rejected, requires review).
*   **Calling Interface:**
    *   WebRTC based dialer.
    *   Make calls to other application users (peer-to-peer or server-mediated).
    *   Make calls to PSTN numbers (US, UK, Nigeria, other international destinations based on subscription).
    *   Contact management (address book).
    *   Call history (view CDRs).
    *   Real-time call quality indicators.
    *   Call controls (mute, hold, transfer - if supported).
*   **SMS Messaging (Optional Service):**
    *   Send SMS messages to US, UK, Nigerian numbers (using assigned DID).
    *   Receive SMS messages (if supported by DID and backend).
    *   View message history.
*   **DID Number Management:**
    *   View assigned DID numbers.
    *   Potentially select outbound Caller ID from assigned DIDs.
*   **User Profile Management:**
    *   Update personal information.
    *   Manage notification preferences.
    *   Security settings (e.g., change password, manage 2FA if implemented).
*   **Billing and Payments:**
    *   View billing history.
    *   Manage payment methods.
    *   Make payments or top-up prepaid balance.

## Tech Stack (Assumed)

*   **React:** For building the user interface.
*   **State Management:** Redux, Zustand, or React Context API.
*   **Routing:** React Router.
*   **API Communication:** Axios or Fetch API to interact with the backend REST APIs.
*   **WebSockets:** For real-time communication (e.g., call signaling, notifications) via Socket.IO or native WebSockets.
*   **WebRTC:** Using browser APIs directly or via a library for call functionality.
*   **Styling:** CSS Modules, Styled Components, Tailwind CSS, or a UI library like Material-UI or Ant Design.

## Setup and Build (Placeholder Commands)

These are typical commands for a Create React App based project.

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
    This will typically start the app on `http://localhost:3000`.
    You might need to configure a proxy in `package.json` or `src/setupProxy.js` to forward API requests to the backend during development (e.g., `/api` to `http://localhost:5000/api`).

3.  **Build for Production:**
    ```bash
    npm run build
    # or
    yarn build
    ```
    This will create an optimized static build in the `build/` or `dist/` directory. The Nginx configuration provided (`nginx.conf`) expects the build output in `/opt/voip-user-app-enhanced/dist`.

## Nginx Configuration

An example Nginx configuration (`nginx.conf`) is provided in this directory. It's designed to:
*   Serve the static React application.
*   Handle client-side routing by redirecting all non-asset requests to `index.html`.
*   Proxy API requests (`/api/`) to the backend Gunicorn servers.
*   Proxy WebSocket connections (`/ws/`) to the backend.
*   Implement SSL/TLS.
*   Set security headers.
*   Enable Gzip compression.
*   Configure static asset caching.

## Further Development

This README and the `nginx.conf` are initial structural files. The actual React components, services, and logic need to be implemented according to the detailed requirements of the VoIP Business Solution.
Key areas for development:
*   API service wrappers for backend communication.
*   WebRTC integration for call handling.
*   WebSocket integration for signaling.
*   UI components for all features listed above.
*   Robust error handling and user feedback.
*   Internationalization (i18n) and Localization (l10n) if supporting multiple languages.
*   Accessibility (a11y) considerations.
*   Comprehensive testing (unit, integration, end-to-end).
