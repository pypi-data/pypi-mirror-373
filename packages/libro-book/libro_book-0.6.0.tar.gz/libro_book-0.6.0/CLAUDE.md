# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important Style Guidelines

- **No emojis**: Do not use emojis in code, documentation, commit messages, or any output.
- Use clear, professional text instead.
- **Clean communication**: Focus on substance over decoration in all written content.

## Project Overview

Libro is a terminal-based tool for tracking personal reading history. It stores book and review data in a local SQLite database and provides an interactive TUI interface as well as traditional CLI commands. The application is built with Python 3.10+, uses Textual for the TUI interface, and Rich for CLI formatting.

## Commands

### Development Commands
- `just install` - Install dependencies using uv
- `just lint` - Run ruff linting and format checks on src/libro/
- `just lint-fix` - Auto-fix ruff formatting issues
- `just type-check` - Run mypy type checking
- `just clean` - Remove build artifacts and Python cache files
- `just build` - Clean, lint, install, and build the package
- `just run <args>` - Run the CLI application with arguments
- `uv run libro <args>` - Alternative way to run the application

### Testing and Quality
- `just lint` - Check code style and formatting (runs ruff check and format --check)
- `just lint-fix` - Automatically fix formatting issues
- `just type-check` - Run mypy type checking
- `just test` - Run the test suite with pytest
- `just ci` - Run all CI checks locally (lint, type-check, test)
- `ruff check src/libro/` - Lint the codebase (configured in pyproject.toml)
- `ruff format src/libro/` - Format code automatically

### Build and Release
- `just publish` - Build and publish to PyPI as `libro-book`
- `py -m build` - Build the package
- `py -m twine upload dist/*` - Upload to PyPI

## Architecture

### Core Structure
- `src/libro/main.py` - Entry point with CLI argument parsing and command routing
- `src/libro/models.py` - Data classes for Book, Review, BookReview, ReadingList, and ReadingListBook
- `src/libro/config.py` - Configuration and argument parsing (defaults to TUI interface)
- `src/libro/tui/` - Interactive TUI components:
  - `app.py` - Main TUI application with search functionality
  - `screens/` - Individual screens (book detail, add book, edit book, reading lists, etc.)
- `src/libro/actions/` - CLI command implementations:
  - `db.py` - Database initialization and migration
  - `show.py` - Display books and reviews
  - `report.py` - Generate reading reports and statistics
  - `modify.py` - Add and edit books/reviews
  - `importer.py` - Import from external sources (Goodreads, CSV)
  - `lists.py` - Reading list management operations

### Database Schema
- `books` table: id, title, author, pages, pub_year, genre
- `reviews` table: id, book_id (FK), date_read, rating, review
- `reading_lists` table: id, name, description, created_date
- `reading_list_books` table: id, list_id (FK), book_id (FK), added_date, priority

### Key Design Patterns
- Uses dataclasses for clean data modeling
- SQLite with row factory for named column access
- Command pattern for CLI actions
- Textual framework for interactive TUI with screens and widgets
- Rich library for CLI terminal formatting and tables

### Database Location Priority
1. `--db` command-line flag
2. `libro.db` in current directory
3. `LIBRO_DB` environment variable
4. Platform-specific data directory

### Package Management
- Uses `uv` for dependency management and virtual environments
- Built with `hatchling` build system
- Published to PyPI as `libro-book` (not `libro` due to naming conflicts)
- Configured for Python 3.10+ compatibility

## Reading Lists Feature

### Overview
Reading lists allow users to organize books into curated collections (e.g., "To Read", "Sci-Fi Classics", "Summer 2025"). Each list can contain multiple books with progress tracking.

### Key Features
- Create, edit, and delete reading lists with names and descriptions
- Add books to lists (creates book if it doesn't exist)
- Remove books from lists (preserves book in database)
- View list contents with read/unread status and progress indicators
- Import books from CSV files directly into lists
- Track reading statistics and completion percentages
- Priority system for ordering books within lists

### CLI Commands
- `libro list` - Show all reading lists with summary stats
- `libro list create <name> [--description]` - Create new reading list
- `libro list show <id>` - Display specific list contents
- `libro list add <id>` - Add book to list (interactive prompts)
- `libro list remove <id> <book_id>` - Remove book from list
- `libro list edit <id> [--name] [--description]` - Edit list details
- `libro list delete <id>` - Delete entire list (preserves books)
- `libro list stats [id]` - Show statistics (all lists or specific list)
- `libro list import <csv_file> [--id|--name] [--description]` - Import CSV to list

### Database Integration
- Automatic database migration adds reading list tables to existing databases
- Foreign key constraints ensure data integrity
- Cascade deletes remove list associations when lists are deleted
- Junction table design allows books to belong to multiple lists

### Data Sources
The `/data/` directory contains JSON files with book metadata for fiction and nonfiction books, used for testing or seeding data. Ignore the `/data/` directory.

## Book Management Commands

### Core Commands
- `libro` or `libro report` - Show books read in current year (default view)
- `libro book` - Show recent books (latest 20 by default)
- `libro book <id>` - Show details for specific book ID
- `libro book add` - Add a new book (without review)
- `libro book edit <id>` - Edit book details

### Book Search and Filtering
The `libro book` command supports multiple search and filtering options:

- `libro book --author <name>` - Find books by author (partial match)
- `libro book --title <title>` - Find books by title (partial match)  
- `libro book --year <year>` - Find books published in specific year

### Design Notes
- The `show` subcommand has been removed - `libro book` defaults to showing books
- Book ID can be passed directly: `libro book 123` instead of `libro book show 123`
- All filtering options work without needing the `show` subcommand

## Review Management Commands

### Core Commands
- `libro review` - Show recent reviews (latest 20 by default)
- `libro review <id>` - Show details for specific review ID
- `libro review add <book_id>` - Add a review to an existing book
- `libro review edit <id>` - Edit review details

### Review Search and Filtering
The `libro review` command supports multiple search and filtering options:

- `libro review --author <name>` - Find reviews for books by author (partial match)
- `libro review --title <title>` - Find reviews for books by title (partial match)
- `libro review --year <year>` - Find reviews made in specific year (by date_read)

### Design Notes
- The `show` subcommand has been removed - `libro review` defaults to showing reviews
- Review ID can be passed directly: `libro review 456` instead of `libro review show 456`
- Year filtering uses the review date (`date_read`), not the book publication year
- Author and title filtering search the associated book details

## Report Commands

### Core Commands
- `libro report` - Show books read in current year (default view)
- `libro report <id>` - Show details for specific review ID
- `libro report --chart` - Show chart view of books read by year
- `libro report --author` - Show author statistics (most read authors)
- `libro report --author "<name>"` - Show books/reviews by specific author

### Year Parameter Behavior
The year parameter behaves differently across commands:

- **`libro report`**: Defaults to current year when no `--year` specified
- **`libro book`**: Shows recent books (latest 20) when no `--year` specified  
- **`libro review`**: Shows recent reviews (latest 20) when no `--year` specified
- **All commands**: Filter by specific year when `--year` is explicitly provided

This design allows the report view to focus on current reading progress while book and review browsers default to showing recently added items across all years.

## Development Workflow

### Code Quality Process
When making code changes, follow this workflow:

1. **Make your changes** to the codebase
2. **Run `just lint`** to check for linting and formatting issues  
3. **Run `just lint-fix`** to automatically fix formatting issues
4. **Run `just type-check`** to verify type annotations are correct
5. **Fix any remaining issues** manually if needed
6. **Test the changes** with `just run <command>` to ensure functionality works

This ensures consistent code style and catches type errors early in the development process.

## Default Interface

As of the latest version, Libro defaults to the interactive TUI interface when no command is specified:
- Running `libro` (with no arguments) launches the TUI interface
- CLI commands are still available by specifying them explicitly (e.g., `libro report`, `libro book add`)

## Development Notes

- **Do not run TUI during development** - The TUI interface uses terminal escape sequences that interfere with Claude Code. Always test CLI commands instead (e.g., `libro report`, `libro book`, etc.)
- Use `uv run libro report` to test functionality without launching the interactive interface


