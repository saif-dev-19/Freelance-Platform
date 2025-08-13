# Freelancer Platform

A backend service for a **freelancer marketplace** built with Django and Django REST Framework (DRF).  
It supports **user authentication**, **service listings**, **order management**, and **seller earnings tracking**.

## Features

- **User Authentication** – Register, login, logout, token-based authentication
- **Role-based Access** – Separate permissions for buyers and sellers
- **Services** – Sellers can create and manage services
- **Orders** – Buyers can place orders for services
- **Order History** – Buyers can view past orders
- **Seller Earnings** – Sellers can view their total earnings
- **Status Tracking** – Order status updates (e.g., pending, completed)

---

## Tech Stack

- **Backend:** Django, Django REST Framework
- **Database:** SQLite (default) or PostgreSQL
- **Authentication:** JWT or Session Authentication
- **Other:** Python 3.13

---

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/saif-dev-19/freelancer-platform.git
cd freelancer-platform
