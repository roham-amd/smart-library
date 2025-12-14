import threading
import time
import random
from collections import deque

class LibrarySystem:
    def __init__(self, num_books, queue_capacity):
        # Shared database
        self.books_inventory = num_books
        self.queue_capacity = queue_capacity
        
        # Request queue for borrowers
        self.request_queue = deque()
        
        # Semaphores and locks for readers-writers problem
        self.read_count = 0
        self.read_count_lock = threading.Lock()
        self.db_access_lock = threading.Lock()  # For writer (librarian) access
        
        # Semaphores for request queue (producer-consumer)
        self.queue_semaphore = threading.Semaphore(queue_capacity)
        self.queue_lock = threading.Lock()
        self.items_available = threading.Semaphore(0)  # Signals librarian when requests exist
        
        # Librarian state
        self.librarian_sleeping = True
        self.librarian_lock = threading.Lock()
        
        # Fair scheduling - prevent writer starvation
        self.writer_waiting = False
        self.writer_lock = threading.Lock()
        
        # System status
        self.active = True
        self.status_lock = threading.Lock()
        
    def print_status(self, message):
        """Thread-safe status printing"""
        with self.status_lock:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
    
    def reader_entry(self, reader_id):
        """Reader enters the reading section"""
        # Wait if writer is waiting (fair scheduling)
        while self.active:
            with self.writer_lock:
                if not self.writer_waiting:
                    break
            time.sleep(0.01)
        
        with self.read_count_lock:
            self.read_count += 1
            if self.read_count == 1:
                # First reader locks database from writers
                self.db_access_lock.acquire()
            self.print_status(f"📖 Reader-{reader_id} entered reading section (Active readers: {self.read_count})")
    
    def reader_exit(self, reader_id):
        """Reader exits the reading section"""
        with self.read_count_lock:
            self.read_count -= 1
            self.print_status(f"📕 Reader-{reader_id} left reading section (Active readers: {self.read_count})")
            if self.read_count == 0:
                # Last reader unlocks database for writers
                self.db_access_lock.release()
    
    def reader_read(self, reader_id):
        """Reader reads the database"""
        self.print_status(f"📚 Reader-{reader_id} is reading book catalog...")
        time.sleep(random.uniform(0.5, 1.5))  # Simulate reading time
        self.print_status(f"✅ Reader-{reader_id} finished reading")
    
    def borrower_submit_request(self, borrower_id):
        """Borrower submits a borrow request"""
        self.print_status(f"📝 Borrower-{borrower_id} wants to borrow a book")
        
        # Try to add to queue (producer)
        acquired = self.queue_semaphore.acquire(timeout=2)
        if not acquired:
            self.print_status(f"⚠️ Borrower-{borrower_id} couldn't add request - queue full!")
            return
        
        with self.queue_lock:
            self.request_queue.append(borrower_id)
            queue_size = len(self.request_queue)
            self.print_status(f"➕ Borrower-{borrower_id} added to queue (Queue size: {queue_size})")
        
        # Wake up librarian if sleeping
        with self.librarian_lock:
            if self.librarian_sleeping:
                self.librarian_sleeping = False
                self.print_status("🔔 Librarian woken up!")
        
        # Signal that an item is available
        self.items_available.release()
    
    def librarian_process_request(self):
        """Librarian processes a borrow request"""
        # Wait for request with timeout
        acquired = self.items_available.acquire(timeout=0.2)
        if not acquired:
            return False
        
        # Get request from queue
        with self.queue_lock:
            if not self.request_queue:
                return False
            borrower_id = self.request_queue.popleft()
            queue_size = len(self.request_queue)
            self.print_status(f"👨‍💼 Librarian processing Borrower-{borrower_id}'s request (Queue: {queue_size})")
        
        # Simulate processing time (searching for book)
        self.print_status(f"⏳ Librarian searching for book for Borrower-{borrower_id}...")
        time.sleep(random.uniform(1, 2))
        
        # Update database (writer access) - signal we're waiting
        with self.writer_lock:
            self.writer_waiting = True
        
        self.print_status(f"🔒 Librarian waiting for database access...")
        
        # Acquire exclusive database access
        self.db_access_lock.acquire()
        
        # We got the lock, no longer waiting
        with self.writer_lock:
            self.writer_waiting = False
        
        # Update inventory
        try:
            if self.books_inventory > 0:
                self.books_inventory -= 1
                self.print_status(f"✅ Librarian gave book to Borrower-{borrower_id} (Books left: {self.books_inventory})")
            else:
                self.print_status(f"❌ No books available for Borrower-{borrower_id}")
        finally:
            # Always release the database lock
            self.db_access_lock.release()
            # Free up queue slot
            self.queue_semaphore.release()
        
        return True
    
    def librarian_rest(self):
        """Librarian goes to rest"""
        with self.librarian_lock:
            if len(self.request_queue) == 0:
                self.librarian_sleeping = True
                self.print_status("💤 Librarian is resting...")

def reader_thread(library, reader_id, request_time):
    """Thread function for readers"""
    time.sleep(random.uniform(0, request_time))
    
    while library.active:
        try:
            library.reader_entry(reader_id)
            library.reader_read(reader_id)
            library.reader_exit(reader_id)
        except Exception as e:
            library.print_status(f"❌ Reader-{reader_id} error: {e}")
        
        # Random delay before next read
        time.sleep(random.uniform(2, 4))

def borrower_thread(library, borrower_id, request_time):
    """Thread function for borrowers"""
    time.sleep(random.uniform(0, request_time))
    
    while library.active:
        try:
            library.borrower_submit_request(borrower_id)
        except Exception as e:
            library.print_status(f"❌ Borrower-{borrower_id} error: {e}")
        
        # Random delay before next borrow attempt
        time.sleep(random.uniform(3, 6))

def librarian_thread(library):
    """Thread function for librarian"""
    while library.active:
        try:
            with library.queue_lock:
                queue_empty = len(library.request_queue) == 0
            
            if queue_empty:
                library.librarian_rest()
                time.sleep(0.1)
            else:
                library.librarian_process_request()
        except Exception as e:
            library.print_status(f"❌ Librarian error: {e}")
            time.sleep(0.1)

def main():
    print("=" * 60)
    print("🏛️  SMART LIBRARY SYSTEM SIMULATION")
    print("=" * 60)
    
    # User inputs
    num_readers = int(input("Enter number of Readers: "))
    num_borrowers = int(input("Enter number of Borrowers: "))
    request_time = float(input("Enter request generation time (seconds): "))
    num_books = int(input("Enter number of available books: "))
    queue_capacity = int(input("Enter request queue capacity: "))
    simulation_time = int(input("Enter simulation duration (seconds): "))
    
    print("\n" + "=" * 60)
    print("🚀 Starting simulation...")
    print("=" * 60 + "\n")
    
    # Initialize library system
    library = LibrarySystem(num_books, queue_capacity)
    
    # Create threads
    threads = []
    
    # Create reader threads
    for i in range(1, num_readers + 1):
        t = threading.Thread(target=reader_thread, args=(library, i, request_time), daemon=True)
        threads.append(t)
        t.start()
    
    # Create borrower threads
    for i in range(1, num_borrowers + 1):
        t = threading.Thread(target=borrower_thread, args=(library, i, request_time), daemon=True)
        threads.append(t)
        t.start()
    
    # Create librarian thread
    lib_thread = threading.Thread(target=librarian_thread, args=(library,), daemon=True)
    threads.append(lib_thread)
    lib_thread.start()
    
    # Run simulation for specified time
    try:
        time.sleep(simulation_time)
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulation interrupted by user")
    
    # Stop simulation
    library.active = False
    time.sleep(1)  # Give threads time to finish
    
    print("\n" + "=" * 60)
    print("🏁 SIMULATION ENDED")
    print("=" * 60)
    print(f"📊 Final Statistics:")
    print(f"   Books remaining: {library.books_inventory}")
    print(f"   Pending requests: {len(library.request_queue)}")
    print(f"   Active readers: {library.read_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()