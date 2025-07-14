## Authentication API

| Endpoint                   | Method | Description                        | Status   |
|----------------------------|--------|------------------------------------|----------|
| `/api/register`            | POST   | Register as a new user             | DONE     |
| `/api/login`               | POST   | Login (admin or user based on role)| NOT DONE |
| `/api/logout`              | POST   | Logout current session/token       | NOT DONE |
| `/api/user/me`             | GET    | Get current user details           | NOT DONE |

## Admin API

| Endpoint                                   | Method | Description                                         | Status   |
|---------------------------------------------|--------|-----------------------------------------------------|----------|
| `/api/admin/dashboard`                      | GET    | View admin dashboard (stats, charts)                | DONE     |
| `/api/admin/users`                          | GET    | View all registered users                           | NOT DONE |
| `/api/admin/parking-lots`                   | POST   | Create a new parking lot with N spots               | NOT DONE |
| `/api/admin/parking-lots`                   | GET    | View all parking lots                               | NOT DONE |
| `/api/admin/parking-lots/<int:lot_id>`      | PUT    | Edit parking lot details                            | NOT DONE |
| `/api/admin/parking-lots/<int:lot_id>`      | DELETE | Delete parking lot (only if all spots are empty)    | NOT DONE |
| `/api/admin/parking-spots/<int:spot_id>`    | GET    | View details of a parking spot                      | NOT DONE |
| `/api/admin/parking-spots/<int:spot_id>`    | DELETE | Delete a spot (only if it’s available)              | NOT DONE |

## User API

| Endpoint                                   | Method | Description                                 | Status   |
|---------------------------------------------|--------|---------------------------------------------|----------|
| `/api/user/dashboard`                      | GET    | View available lots and spot status         | DONE     |
| `/api/user/reserve`                        | POST   | Reserve a parking spot (auto-assigned)      | NOT DONE |
| `/api/user/vacate/<int:reservation_id>`    | PUT    | Vacate the spot and calculate cost          | NOT DONE |
| `/api/user/history`                        | GET    | View all past and current reservations      | NOT DONE |
| `/api/user/report/monthly`                 | GET    | Get monthly HTML/PDF parking report         | NOT DONE |
| `/api/user/export-csv`                     | POST   | Trigger CSV export of user history          | NOT DONE |
| `/api/user/download-csv/<job_id>`          | GET    | Download completed CSV report               | NOT DONE |