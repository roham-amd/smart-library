# Smart Library System 🏛️

A Python simulation of a smart library system demonstrating concurrent programming concepts. This project implements three classic synchronization problems: **Readers-Writers**, **Producer-Consumer**, and **Sleeping Barber** patterns using thread synchronization, semaphores, and locks.

## Project Overview

This simulation models a library system with three types of actors:
- **Readers**: Access the book database for reading (read-only)
- **Borrowers**: Submit book borrowing requests
- **Librarian**: Processes borrowing requests and updates the database

## System Components

### 1. Users (Reader / Borrower)

#### Readers
- Have read-only access to the library database
- Multiple readers can simultaneously access the reading section
- Entry of writers (librarian) does not cause starvation of readers
- Implemented using the Readers-Writers pattern with fair scheduling

#### Borrowers
- Submit "book borrowing" requests
- Requests enter a bounded request queue (Producer-Consumer pattern)
- Must wait for the librarian to process their requests
- Queue has configurable capacity

### 2. Librarian
- Rests when the request queue is empty (Sleeping Barber pattern)
- Wakes up automatically when a request arrives
- Processes requests with time-consuming operations (simulated with sleep)
- Updates the book inventory (database write operation)
- Ensures exclusive database access during updates

### 3. Shared Database (Book Database)
- Readable simultaneously by multiple readers
- Writable only by the librarian when no active readers are present
- Updated (inventory write) by the librarian while processing requests
- Protected by locks to prevent race conditions

## Features

✅ **Thread Safety**: Uses locks and semaphores to prevent race conditions  
✅ **Deadlock Prevention**: Careful lock ordering and timeout mechanisms  
✅ **Starvation Prevention**: Fair scheduling between readers and writers  
✅ **Concurrent Access**: Multiple readers can access simultaneously  
✅ **Bounded Queue**: Producer-Consumer pattern with configurable capacity  
✅ **Real-time Status**: Clear system status messages with timestamps  

## Prerequisites

- Docker installed on your system
- Or Python 3.11+ if running without Docker

## Running with Docker

### Step 1: Build the Docker Image

```bash
docker build -t smart-library .
```

### Step 2: Run the Container

```bash
docker run -it smart-library
```

The application will prompt you for the following inputs:
- **Number of Readers**: How many reader threads to create
- **Number of Borrowers**: How many borrower threads to create
- **Request generation time**: Delay before threads start (in seconds)
- **Number of available books**: Initial book inventory
- **Request queue capacity**: Maximum number of simultaneous requests (e.g., 5)
- **Simulation duration**: How long to run the simulation (in seconds)

### Example Run

```bash
$ docker run -it smart-library
Enter number of Readers: 3
Enter number of Borrowers: 2
Enter request generation time: 1.0
Enter number of available books: 10
Enter request queue capacity: 5
Enter simulation duration: 30
```

## Running Without Docker

If you prefer to run directly with Python:

```bash
python main.py
```

## Configuration Options

| Parameter | Description | Example |
|-----------|-------------|---------|
| Number of Readers | Concurrent reader threads | 3-10 |
| Number of Borrowers | Concurrent borrower threads | 2-5 |
| Request generation time | Initial delay before threads start | 0.5-2.0 seconds |
| Number of available books | Initial book inventory | 5-20 |
| Request queue capacity | Max simultaneous requests | 3-10 |
| Simulation duration | How long to run | 30-120 seconds |

## Expected Output

The system prints real-time status messages showing:

- 📖 Reader entry/exit from reading section
- 📚 Reader reading activities
- 📝 Borrower request submissions
- ➕ Queue status updates
- 👨‍💼 Librarian processing activities
- 🔒 Database access control
- ✅ Book delivery confirmations
- 💤 Librarian resting state
- 📊 Final statistics

### Sample Output

```
============================================================
🏛️  SMART LIBRARY SYSTEM SIMULATION
============================================================
[14:30:15] 📖 Reader-1 entered reading section (Active readers: 1)
[14:30:15] 📚 Reader-1 is reading book catalog...
[14:30:16] 📝 Borrower-1 wants to borrow a book
[14:30:16] ➕ Borrower-1 added to queue (Queue size: 1)
[14:30:16] 🔔 Librarian woken up!
[14:30:16] 👨‍💼 Librarian processing Borrower-1's request (Queue: 0)
[14:30:16] ⏳ Librarian searching for book for Borrower-1...
[14:30:18] 🔒 Librarian waiting for database access...
[14:30:18] ✅ Librarian gave book to Borrower-1 (Books left: 9)
...
```

## Implementation Details

### Synchronization Mechanisms

1. **Readers-Writers Pattern**
   - `read_count_lock`: Protects reader count
   - `db_access_lock`: Exclusive lock for database writes
   - `writer_waiting`: Flag to prevent writer starvation

2. **Producer-Consumer Pattern**
   - `queue_semaphore`: Bounds the request queue
   - `queue_lock`: Protects queue operations
   - `items_available`: Signals librarian when requests exist

3. **Sleeping Barber Pattern**
   - `librarian_sleeping`: Tracks librarian state
   - Automatic wake-up on request arrival

### Safety Features

- **Deadlock Prevention**: Timeout mechanisms and careful lock ordering
- **Race Condition Prevention**: All shared resources protected by locks
- **Starvation Prevention**: Fair scheduling ensures both readers and writers get access
- **Thread Safety**: All print operations are synchronized

## Project Structure

```
smart-library/
├── main.py          # Main application code
├── Dockerfile       # Docker configuration
└── README.md        # This file
```

## License

This project is for educational purposes, demonstrating concurrent programming concepts.

---

**Note**: This simulation is designed for educational purposes to demonstrate thread synchronization, semaphores, and classic concurrency problems in computer science.
