"""
Todo.sh operations orchestration and business logic.
"""

from datetime import datetime
from typing import Any, Optional


class TodoManager:
    """Orchestrates todo.sh operations with business logic."""

    def __init__(self, todo_shell: Any) -> None:
        self.todo_shell = todo_shell

    def add_task(
        self,
        description: str,
        priority: Optional[str] = None,
        project: Optional[str] = None,
        context: Optional[str] = None,
        due: Optional[str] = None,
        recurring: Optional[str] = None,
        duration: Optional[str] = None,
    ) -> str:
        """Add new task with explicit project/context parameters."""
        # Validate and sanitize inputs
        if priority and not (
            len(priority) == 1 and priority.isalpha() and priority.isupper()
        ):
            raise ValueError(
                f"Invalid priority '{priority}'. Must be a single uppercase letter (A-Z)."
            )

        if project:
            # Remove any existing + symbols to prevent duplication
            project = project.strip().lstrip("+")
            if not project:
                raise ValueError(
                    "Project name cannot be empty after removing + symbol."
                )

        if context:
            # Remove any existing @ symbols to prevent duplication
            context = context.strip().lstrip("@")
            if not context:
                raise ValueError(
                    "Context name cannot be empty after removing @ symbol."
                )

        if due:
            # Basic date format validation
            try:
                datetime.strptime(due, "%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    f"Invalid due date format '{due}'. Must be YYYY-MM-DD."
                )

        if recurring:
            # Validate recurring format
            if not recurring.startswith("rec:"):
                raise ValueError(
                    f"Invalid recurring format '{recurring}'. Must start with 'rec:'."
                )
            # Basic validation of recurring syntax
            parts = recurring.split(":")
            if len(parts) < 2 or len(parts) > 3:
                raise ValueError(
                    f"Invalid recurring format '{recurring}'. Expected 'rec:frequency' or 'rec:frequency:interval'."
                )
            frequency = parts[1]
            if frequency not in ["daily", "weekly", "monthly", "yearly"]:
                raise ValueError(
                    f"Invalid frequency '{frequency}'. Must be one of: daily, weekly, monthly, yearly."
                )
            if len(parts) == 3:
                try:
                    interval = int(parts[2])
                    if interval < 1:
                        raise ValueError("Interval must be at least 1.")
                except ValueError:
                    raise ValueError(
                        f"Invalid interval '{parts[2]}'. Must be a positive integer."
                    )

        if duration is not None:
            # Validate duration format (e.g., "30m", "2h", "1d")
            if not duration or not isinstance(duration, str):
                raise ValueError("Duration must be a non-empty string.")

            # Check if duration ends with a valid unit
            if not any(duration.endswith(unit) for unit in ["m", "h", "d"]):
                raise ValueError(
                    f"Invalid duration format '{duration}'. Must end with m (minutes), h (hours), or d (days)."
                )

            # Extract the numeric part and validate it
            value = duration[:-1]
            if not value:
                raise ValueError("Duration value cannot be empty.")

            try:
                # Check if the value is a valid positive number
                numeric_value = float(value)
                if numeric_value <= 0:
                    raise ValueError("Duration value must be positive.")
            except ValueError:
                raise ValueError(
                    f"Invalid duration value '{value}'. Must be a positive number."
                )

        # Build the full task description with priority, project, and context
        full_description = description

        if priority:
            full_description = f"({priority}) {full_description}"

        if project:
            full_description = f"{full_description} +{project}"

        if context:
            full_description = f"{full_description} @{context}"

        if due:
            full_description = f"{full_description} due:{due}"

        if recurring:
            full_description = f"{full_description} {recurring}"

        if duration:
            full_description = f"{full_description} duration:{duration}"

        self.todo_shell.add(full_description)
        return f"Added task: {full_description}"

    def list_tasks(self, filter: Optional[str] = None) -> str:
        """List tasks with optional filtering."""
        result = self.todo_shell.list_tasks(filter)
        if not result.strip():
            return "No tasks found."

        # Return the raw todo.txt format for the LLM to format conversationally
        # The LLM will convert this into natural language in its response
        return result

    def complete_task(self, task_number: int) -> str:
        """Mark task complete by line number."""
        result = self.todo_shell.complete(task_number)
        return f"Completed task {task_number}: {result}"

    def get_overview(self, **kwargs: Any) -> str:
        """Show current task statistics."""
        tasks = self.todo_shell.list_tasks()
        completed = self.todo_shell.list_completed()

        task_count = (
            len([line for line in tasks.split("\n") if line.strip()])
            if tasks.strip()
            else 0
        )
        completed_count = (
            len([line for line in completed.split("\n") if line.strip()])
            if completed.strip()
            else 0
        )

        return f"Task Overview:\n- Active tasks: {task_count}\n- Completed tasks: {completed_count}"

    def replace_task(self, task_number: int, new_description: str) -> str:
        """Replace entire task content."""
        result = self.todo_shell.replace(task_number, new_description)
        return f"Replaced task {task_number}: {result}"

    def append_to_task(self, task_number: int, text: str) -> str:
        """Add text to end of existing task."""
        result = self.todo_shell.append(task_number, text)
        return f"Appended to task {task_number}: {result}"

    def prepend_to_task(self, task_number: int, text: str) -> str:
        """Add text to beginning of existing task."""
        result = self.todo_shell.prepend(task_number, text)
        return f"Prepended to task {task_number}: {result}"

    def delete_task(self, task_number: int, term: Optional[str] = None) -> str:
        """Delete entire task or specific term from task."""
        result = self.todo_shell.delete(task_number, term)
        if term:
            return f"Removed '{term}' from task {task_number}: {result}"
        else:
            return f"Deleted task {task_number}: {result}"

    def set_priority(self, task_number: int, priority: str) -> str:
        """Set or change task priority (A-Z)."""
        result = self.todo_shell.set_priority(task_number, priority)
        return f"Set priority {priority} for task {task_number}: {result}"

    def remove_priority(self, task_number: int) -> str:
        """Remove priority from task."""
        result = self.todo_shell.remove_priority(task_number)
        return f"Removed priority from task {task_number}: {result}"

    def set_due_date(self, task_number: int, due_date: str) -> str:
        """
        Set or update due date for a task by intelligently rewriting it.

        Args:
            task_number: The task number to modify
            due_date: Due date in YYYY-MM-DD format, or empty string to remove due date

        Returns:
            Confirmation message with the updated task
        """
        # Validate due date format only if not empty
        if due_date.strip():
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError(
                    f"Invalid due date format '{due_date}'. Must be YYYY-MM-DD."
                )

        result = self.todo_shell.set_due_date(task_number, due_date)
        if due_date.strip():
            return f"Set due date {due_date} for task {task_number}: {result}"
        else:
            return f"Removed due date from task {task_number}: {result}"

    def set_context(self, task_number: int, context: str) -> str:
        """
        Set or update context for a task by intelligently rewriting it.

        Args:
            task_number: The task number to modify
            context: Context name (without @ symbol), or empty string to remove context

        Returns:
            Confirmation message with the updated task
        """
        # Validate context name if not empty
        if context.strip():
            # Remove any existing @ symbols to prevent duplication
            clean_context = context.strip().lstrip("@")
            if not clean_context:
                raise ValueError(
                    "Context name cannot be empty after removing @ symbol."
                )

        result = self.todo_shell.set_context(task_number, context)
        if context.strip():
            clean_context = context.strip().lstrip("@")
            return f"Set context @{clean_context} for task {task_number}: {result}"
        else:
            return f"Removed context from task {task_number}: {result}"

    def set_project(self, task_number: int, projects: list) -> str:
        """
        Set or update projects for a task by intelligently rewriting it.

        Args:
            task_number: The task number to modify
            projects: List of project operations. Each item can be:
                     - "project" (add project)
                     - "-project" (remove project)
                     - Empty string removes all projects

        Returns:
            Confirmation message with the updated task
        """
        # Validate project names if not empty
        if projects:
            for project in projects:
                if project.strip() and not project.startswith("-"):
                    # Remove any existing + symbols to prevent duplication
                    clean_project = project.strip().lstrip("+")
                    if not clean_project:
                        raise ValueError(
                            "Project name cannot be empty after removing + symbol."
                        )
                elif project.startswith("-"):
                    clean_project = project[1:].strip().lstrip("+")
                    if not clean_project:
                        raise ValueError(
                            "Project name cannot be empty after removing - and + symbols."
                        )

        result = self.todo_shell.set_project(task_number, projects)

        if not projects:
            return f"No project changes made to task {task_number}: {result}"
        else:
            # Build operation description
            operations = []
            for project in projects:
                if not project.strip():
                    # Empty string is a NOOP - skip
                    continue
                elif project.startswith("-"):
                    clean_project = project[1:].strip().lstrip("+")
                    operations.append(f"removed +{clean_project}")
                else:
                    clean_project = project.strip().lstrip("+")
                    operations.append(f"added +{clean_project}")

            if not operations:
                return f"No project changes made to task {task_number}: {result}"
            else:
                operation_desc = ", ".join(operations)
                return f"Updated projects for task {task_number} ({operation_desc}): {result}"

    def list_projects(self, **kwargs: Any) -> str:
        """List all available projects in todo.txt."""
        result = self.todo_shell.list_projects()
        if not result.strip():
            return "No projects found."
        return result

    def list_contexts(self, **kwargs: Any) -> str:
        """List all available contexts in todo.txt."""
        result = self.todo_shell.list_contexts()
        if not result.strip():
            return "No contexts found."
        return result

    def list_completed_tasks(
        self,
        filter: Optional[str] = None,
        project: Optional[str] = None,
        context: Optional[str] = None,
        text_search: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """List completed tasks with optional filtering.

        Args:
            filter: Raw filter string (e.g., '+work', '@office')
            project: Filter by project (without + symbol)
            context: Filter by context (without @ symbol)
            text_search: Search for text in task descriptions
            date_from: Filter tasks completed from this date (YYYY-MM-DD)
            date_to: Filter tasks completed until this date (YYYY-MM-DD)
        """
        # Build filter string from individual parameters
        filter_parts = []

        if filter:
            filter_parts.append(filter)

        if project:
            filter_parts.append(f"+{project}")

        if context:
            filter_parts.append(f"@{context}")

        if text_search:
            filter_parts.append(text_search)

        # Handle date filtering - todo.sh supports direct date pattern matching
        # LIMITATIONS: Due to todo.sh constraints, complex date ranges are not supported.
        # The filtering behavior is:
        # - date_from + date_to: Uses year-month pattern (YYYY-MM) from date_from for month-based filtering
        # - date_from only: Uses exact date pattern (YYYY-MM-DD) for precise date matching
        # - date_to only: Uses year-month pattern (YYYY-MM) from date_to for month-based filtering
        # - Complex ranges spanning multiple months are not supported by todo.sh
        if date_from and date_to:
            # For a date range, we'll use the year-month pattern from date_from
            # This will match all tasks in that month
            filter_parts.append(date_from[:7])  # YYYY-MM format
        elif date_from:
            # For single date, use the full date pattern
            filter_parts.append(date_from)
        elif date_to:
            # For end date only, we'll use the year-month pattern
            # This will match all tasks in that month
            filter_parts.append(date_to[:7])  # YYYY-MM format

        # Combine all filters
        combined_filter = " ".join(filter_parts) if filter_parts else None

        result = self.todo_shell.list_completed(combined_filter)
        if not result.strip():
            return "No completed tasks found matching the criteria."
        return result

    def move_task(
        self, task_number: int, destination: str, source: Optional[str] = None
    ) -> str:
        """Move task from source to destination file."""
        result = self.todo_shell.move(task_number, destination, source)
        return f"Moved task {task_number} to {destination}: {result}"

    def archive_tasks(self, **kwargs: Any) -> str:
        """Archive completed tasks."""
        result = self.todo_shell.archive()
        return f"Archived tasks: {result}"

    def deduplicate_tasks(self, **kwargs: Any) -> str:
        """Remove duplicate tasks."""
        result = self.todo_shell.deduplicate()
        return f"Deduplicated tasks: {result}"

    def get_current_datetime(self, **kwargs: Any) -> str:
        """Get the current date and time."""
        now = datetime.now()
        week_number = now.isocalendar()[1]
        timezone = now.astimezone().tzinfo
        return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')} {timezone} ({now.strftime('%A, %B %d, %Y at %I:%M %p')}) - Week {week_number}"
