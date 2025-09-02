from fild_ui import Browser


class Command:
    GET_ALL = """
        return new Promise((resolve, reject) => {{
            let request = indexedDB.open("{0}");  
            
            request.onsuccess = function(event) {{
                let db = event.target.result;
                let transaction = db.transaction("{1}", "readonly"); 
                let store = transaction.objectStore("{1}");
                let allRecords = store.getAll();
                let dict = {{}};

                let cursorRequest = store.openCursor();
                cursorRequest.onsuccess = function(event) {{
                    let cursor = event.target.result;
                    if (cursor) {{
                        // Convert composite key (array or object) into a string key
                        let key = typeof cursor.key === 'object' 
                            ? JSON.stringify(cursor.key) 
                            : String(cursor.key);
                        dict[cursor.key] = cursor.value;
                        cursor.continue();
                    }} else {{
                        resolve(dict);  // Done reading all entries
                    }}
                }};
                cursorRequest.onerror = function() {{
                    reject("Cursor error reading IndexedDB");
                }};
            }};
            request.onerror = function() {{
                reject("IndexedDB open failed");
            }};
        }});
    """
    DELETE_ALL = """
        return new Promise((resolve, reject) => {{
            let request = indexedDB.open("{0}");
        
            request.onupgradeneeded = function(event) {{
                // Database exists but doesn't contain the object store
                const db = event.target.result;
                if (!db.objectStoreNames.contains("{1}")) {{
                    // Do not create the store; abort
                    event.target.transaction.abort();
                }}
            }};
        
            request.onsuccess = function(event) {{
                let db = event.target.result;
        
                if (!db.objectStoreNames.contains("{1}")) {{
                    db.close();
                    resolve("Object store does not exist; nothing to delete.");
                    return;
                }}
        
                let transaction = db.transaction("{1}", "readwrite");
                let store = transaction.objectStore("{1}");
                let deleteRequest = store.clear();
        
                deleteRequest.onsuccess = function() {{
                    resolve("Deletion successful");
                }};
                deleteRequest.onerror = function(e) {{
                    reject("Error deleting records: " + e.target.error);
                }};
            }};
        
            request.onerror = function(e) {{
                resolve("Database could not be opened; assuming it doesn't exist.");
            }};
        }});
    """
    CREATE_NEW = """
        return new Promise((resolve, reject) => {{
            let request = indexedDB.open("{0}"); 

            request.onsuccess = function(event) {{
                let db = event.target.result;
                let transaction = db.transaction("{1}", "readwrite");
                let store = transaction.objectStore("{1}");
                let insertRequest = store.add({2});
                
                insertRequest.onsuccess = function() {{
                    resolve("Insertion successful");
                }};
                insertRequest.onerror = function(event) {{
                    reject("Error inserting record: " + event.target.error);
                }};
            }};

            request.onerror = function() {{
                reject("IndexedDB open failed");
            }};
        }});
    """


class IndexedDb:
    def __init__(self, name):
        self.name = name

    def get_all_records(self, table_name):
        return Browser().driver.execute_script(
            Command.GET_ALL.format(self.name, table_name)
        )

    def delete_all_records(self, table_name):
        return Browser().driver.execute_script(
            Command.DELETE_ALL.format(self.name, table_name)
        )

    def insert_record(self, table_name, record_json):
        return Browser().driver.execute_script(
            Command.CREATE_NEW.format(self.name, table_name, record_json)
        )
