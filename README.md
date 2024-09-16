# Eventure

## Back-End Endpoints


### Authentication
| Method	| Endpoint	| Description |
| :---      | :---      | :---        |
| POST | /api/register/ | Register a new user |
| POST | /api/login/	| Login and retrieve authentication token |
| POST | /api/logout/	| Logout and revoke authentication token |
| POST | /api/token/	| Retrive authentication token |
| POST | /api/request-password-reset/	| Ask request when forget the password |
| POST | /api/change-password/	| Change the password |
| POST | /api/confirm-password-reset/	| Confirm to change password |


### User and Profile Endpoints
| Method | Endpoint | Description |
| :----- | :---     | :---        |
| POST | /api/login/| Login the user and return an authentication token |
| GET | /api/profile/ | Retrieve the authenticated user's profile |
| PUT | /api/profile/ | Update the authenticated user's profile |
| PATCH |	/api/profile/ | Partially update the authenticated user's profile
| POST |	/api/profile/ | Create a profile for the authenticated user (if it doesn't exist) |


### Event Endpoints

| Method | Endpoint | Description |
| :--    | :----    | :-------    |
| GET	 | /api/event/	| List all events for the authenticated user |
| POST	 | /api/event/	| Create a new event |
| GET	 | /api/event/{id}/	| Retrieve details of a specific event |
| PUT	 | /api/event/{id}/	| Update a specific event |
| PATCH	 | /api/event/{id}/	| Partially update a specific event |
| DELETE | /api/event/{id}/	| Delete a specific event |
| GET	 | /api/event/{id}/weather/	| Get the weather information for a specific offline event |
| GET	 | /api/event/{id}/route/	| Get the best route to a specific event location |