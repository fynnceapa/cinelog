# CineLog - Distributed Movie Journaling System

CineLog is a distributed web application designed for movie enthusiasts to track their watch history, follow friends, and receive real-time notifications about community activity. The project utilizes a modern distributed architecture to handle authentication, search, and background processing.

## ⚠️ Disclaimer: Frontend Development
Please note that the current User Interface (HTML/CSS/JS) is strictly a **Proof of Concept**. I am still working on the front end part and it is currently used only to demonstrate the underlying backend functionality, API integration, and distributed systems architecture.

## 🚀 Tech Stack
* **Backend:** Django 5.0+
* **Database:** PostgreSQL 16
* **Identity Provider:** Keycloak 24.0.0 (OIDC)
* **Search Engine:** Elasticsearch 7.17.9
* **Message Broker:** RabbitMQ 3-management
* **Background Workers:** Custom Python consumers for reviews and notifications
* **Testing:** Mailhog for SMTP email capture

## 🛠️ How to Run the Application

### Development (using Docker Compose)
To start the entire environment for development purposes:

```
docker-compose up --build
```

### Docker Swarm
For a distributed deployment with high availability:
1. Initialize Swarm: ```docker swarm init```
2. Deploy the stack:

```
docker stack deploy -c docker-stack.yml proiect_scd
```

The stack configuration deploys 3 replicas for the web service and 2 replicas for each background worker to ensure load balancing and fault tolerance.


## ⚙️ Background Workers & Distributed Processing
CineLog uses a distributed task processing model to handle time-consuming operations asynchronously, ensuring the web interface remains fast and responsive.

### How it Works:
1.  **Event Trigger**: When a user performs an action (like posting a review or following someone), the web application publishes a JSON message to a corresponding RabbitMQ queue instead of processing it immediately.
2.  **Queue Orchestration**: RabbitMQ acts as the message broker, holding these tasks in `reviews_queue` and `notifications_queue`.
3.  **Worker Consumption**: Independent worker services (running in their own containers) consume these messages and execute the logic in the background.

### Worker Types:
* **Review Worker**: Listens for new movie reviews. It extracts data from the queue and saves the review to the PostgreSQL database, decoupling database writes from the user request.
* **Notification Worker**: Handles system alerts. For example, when a user is followed, it renders an email template and sends it via the SMTP server (Mailhog).

### Purpose & Benefits:
* **Responsiveness**: The user doesn't have to wait for emails to be sent or complex data to be saved before receiving a confirmation on the site.
* **Scalability**: Multiple worker replicas (configured in `docker-stack.yml`) can process the queue in parallel, handling high traffic loads efficiently.

## 🧪 Testing & Utility Commands
The project includes several custom Django management commands located in `core/management/commands` to facilitate testing and system reliability:

* **`test_queue_spam`**: Simulates a high-load scenario by automatically publishing 50 random reviews to the RabbitMQ queue. This is used to verify the asynchronous processing and scalability of the workers.
* **`delete_admin_reviews`**: A cleanup utility that removes all movie reviews created by the 'admin' account, helping maintain a clean database during testing phases.
* **`wait_for_db`**: A crucial startup script that pauses backend execution until the PostgreSQL database is fully reachable. It prevents application crashes during the initial Docker container orchestration.

## 🔐 Keycloak Configuration Guide

CineLog uses Keycloak for centralized authentication via OpenID Connect (OIDC).

### 1. Database Initialization
Keycloak requires a dedicated database. This is automated in our setup:
* The `init-db/init.sql` script contains the `CREATE DATABASE keycloak;` command.
* In `docker-compose.yml`, this script is mounted to `/docker-entrypoint-initdb.d`, ensuring the database is created automatically when the PostgreSQL container starts for the first time.

### 2. Manual Keycloak Setup
Access Keycloak at `http://localhost:8080` with the admin credentials (default: `admin`/`admin`):

1.  **Create a Realm**: Name it `cinelog`.
2.  **Create a Client**:
    * **Client ID**: `cinelog_backend`.
    * **Client Authentication**: Enabled (Confidential).
    * **Valid Redirect URIs**: `http://localhost:8000/oidc/callback/`.
    * **Web Origins**: `*` or `http://localhost:8000`.
3.  **Client Secret**: Copy the secret from the "Credentials" tab and update the `OIDC_RP_CLIENT_SECRET` environment variable in your deployment configuration (`docker-stack.yml` or your local environment).