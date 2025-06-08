# Meeting Scheduler API

## Description
A FastAPI-based meeting scheduler application that allows users to manage meeting slots, check availability, and book meetings. The application stores user busy intervals in memory, suggests available time slots for meetings, and provides user-specific calendar views. The workday is defined as 09:00–18:00 IST.

## Reflection Questions

### Question: If given two more days, what would you refactor or add first, and why?

### Answer
If given two additional days, I would prioritize the following enhancements:

- **Adding Email Reminders**: Implementing email reminders to notify participants in advance, improving meeting attendance and time management.
- **Authentication for Company Employees**: Adding secure login functionality to ensure only authorized users can schedule or view meetings.
- **Meet Link Mailer to All Participants**: Automating the distribution of meeting links to all available participants via email to streamline the process and reduce manual errors.
- **Database Integration**: Incorporating a database to store meeting data, enabling persistence, retrieval, and scalability of the application.


### Question: While developing this application, I leveraged AI tools such as Grok and GitHub Copilot to accelerate development and assist with utility functions.

### Answer
### Tools Used
- **Grok**: For exploring logic suggestions and refining backend workflow.
- **GitHub Copilot**: For auto-generating boilerplate code and helper functions.

### Prompts:
- Generated helper functions like `parse_time()` and `format_time()` to handle user input and display time in readable formats.
- Utilized Copilot to quickly draft API endpoint templates and validate form data.

### Successes
- Saved significant time by automating repetitive code writing.
- Received quick suggestions for handling edge cases and formatting logic.

### Failures
- Occasionally, AI-generated code was incompatible with the framework version or included unused variables, requiring manual fixes.
- Required thorough review of AI-generated logic for accuracy and security, particularly in authentication and validation components.

## API Routes
| Method | Endpoint                     | Description                                                                 |
|--------|------------------------------|-----------------------------------------------------------------------------|
| POST   | `/slots`                     | Accepts a JSON list of users with their busy intervals (ISO-8601 or HH:MM). |
| GET    | `/suggest?duration={minutes}`| Returns the first three time ranges where all users are free for the given duration. |
| GET    | `/calendar/{userId}`         | Returns the specified user's busy slots and booked meetings.                |
| POST   | `/book`                      | Books a meeting for a specified time slot.                                  |

## Installation Setup
### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Steps
1. **Clone the Repository**
   ```bash
   git clone https://github.com/aditya-Kumar421/meetPlanner.git
   cd meeting-scheduler
2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
3. **Run the Application**
   ```bash
   uvicorn main:app --reload

## API Access
The API will be available at `http://localhost:8000`.

### Access API Documentation
Open `http://localhost:8000/docs` in your browser to view the interactive Swagger UI for testing the API.

## Notes
- The application assumes a workday from 09:00 to 18:00 IST.
- Busy intervals and booked meetings are stored in memory and will reset on application restart.
- Time inputs can be in ISO-8601 format (e.g., `2025-06-09T10:00:00+05:30`) or simple HH:MM format (e.g., `10:00`).
- The `/suggest` endpoint returns time ranges in HH:MM–HH:MM format for simplicity.