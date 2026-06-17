PRAGMA foreign_keys = ON;

-- Branches
CREATE TABLE IF NOT EXISTS branches (
  id TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
INSERT OR IGNORE INTO branches (id,label) VALUES ('fourways','Fourways Mall');
INSERT OR IGNORE INTO branches (id,label) VALUES ('rosebank','Rosebank');

-- Customers (simple)
CREATE TABLE IF NOT EXISTS customers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  phone TEXT DEFAULT '',
  email TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Bookings: party bookings (1up_bk_*)
CREATE TABLE IF NOT EXISTS bookings (
  id TEXT PRIMARY KEY,
  legacy_id TEXT,
  branch_id TEXT NOT NULL REFERENCES branches(id),
  source TEXT NOT NULL DEFAULT 'staff',
  booking_type TEXT NOT NULL CHECK (booking_type IN ('party','event','freestyle','venue')),
  status TEXT NOT NULL DEFAULT 'pending',
  customer_id TEXT REFERENCES customers(id),
  customer_name TEXT DEFAULT '',
  customer_phone TEXT DEFAULT '',
  customer_email TEXT DEFAULT '',
  event_type TEXT DEFAULT '',
  package_name TEXT DEFAULT '',
  date TEXT DEFAULT '',
  end_date TEXT DEFAULT '',
  timeslot TEXT DEFAULT '',
  start_time TEXT DEFAULT '',
  end_time TEXT DEFAULT '',
  price REAL DEFAULT 0,
  deposit REAL DEFAULT 0,
  vat_opt TEXT DEFAULT 'none',
  notes TEXT DEFAULT '',
  areas TEXT NOT NULL DEFAULT '[]',
  services TEXT NOT NULL DEFAULT '[]',
  extras TEXT NOT NULL DEFAULT '[]',
  raw_data TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Venue bookings (1up_venue_*) - maybe same as bookings with booking_type venue/event/freestyle
-- We'll keep separate for clarity but could unify.
CREATE TABLE IF NOT EXISTS venue_bookings (
  id TEXT PRIMARY KEY,
  legacy_id TEXT,
  branch_id TEXT NOT NULL REFERENCES branches(id),
  source TEXT NOT NULL DEFAULT 'staff',
  booking_type TEXT NOT NULL CHECK (booking_type IN ('party','event','freestyle','venue')),
  status TEXT NOT NULL DEFAULT 'pending',
  customer_id TEXT REFERENCES customers(id),
  customer_name TEXT DEFAULT '',
  customer_phone TEXT DEFAULT '',
  customer_email TEXT DEFAULT '',
  event_type TEXT DEFAULT '',
  package_name TEXT DEFAULT '',
  date TEXT DEFAULT '',
  end_date TEXT DEFAULT '',
  timeslot TEXT DEFAULT '',
  start_time TEXT DEFAULT '',
  end_time TEXT DEFAULT '',
  price REAL DEFAULT 0,
  deposit REAL DEFAULT 0,
  vat_opt TEXT DEFAULT 'none',
  notes TEXT DEFAULT '',
  areas TEXT NOT NULL DEFAULT '[]',
  services TEXT NOT NULL DEFAULT '[]',
  extras TEXT NOT NULL DEFAULT '[]',
  raw_data TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Stock inventory (1up_stock_*)
CREATE TABLE IF NOT EXISTS stock_items (
  id TEXT PRIMARY KEY,
  branch_id TEXT NOT NULL REFERENCES branches(id),
  name TEXT NOT NULL,
  category TEXT,
  quantity REAL NOT NULL DEFAULT 0,
  reorder_level REAL NOT NULL DEFAULT 0,
  raw_data TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Invoice counter
CREATE TABLE IF NOT EXISTS invoice_counter (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  value INTEGER NOT NULL DEFAULT 1
);
INSERT OR IGNORE INTO invoice_counter (id,value) VALUES (1,1);

-- Settings
CREATE TABLE IF NOT EXISTS settings (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  open_time TEXT DEFAULT '09:00',
  close_time TEXT DEFAULT '18:00',
  duration TEXT DEFAULT '4',
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
INSERT OR IGNORE INTO settings (id,open_time,close_time,duration) VALUES (1,'09:00','18:00','4');

-- WhatsApp templates
CREATE TABLE IF NOT EXISTS wa_templates (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  party TEXT DEFAULT '',
  event TEXT DEFAULT '',
  freestyle TEXT DEFAULT '',
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
INSERT OR IGNORE INTO wa_templates (id,party,event,freestyle) VALUES (1,'','','');

-- Sync log (optional)
CREATE TABLE IF NOT EXISTS sync_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  action TEXT NOT NULL,
  entity TEXT NOT NULL,
  entity_id TEXT DEFAULT '',
  details TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);