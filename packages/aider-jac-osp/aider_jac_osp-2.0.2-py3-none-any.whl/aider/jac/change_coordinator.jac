# change_coordinator_syntax.jac
# Multi-file change coordination walker - Syntax-corrected version
# Coordinates complex multi-file changes with validation and rollback support

# Node definitions
node ChangeRecord {}
node TransactionRecord {}
node PatchRecord {}

walker ChangeCoordinator {

    # Create a new transaction with multiple file changes
    def create_transaction(file_changes: list, description: str) -> dict {
        transaction_id = "txn_" + str(len(file_changes)) + "_" + str(42);  # Simple ID generation
        
        transaction = {
            "id": transaction_id,
            "description": description,
            "changes": file_changes,
            "status": "created",
            "created_time": "2024-01-01T00:00:00Z",  # Placeholder timestamp
            "total_files": len(file_changes),
            "validation_status": "pending",
            "rollback_available": false
        };
        
        print("Created transaction: " + transaction_id);
        print("Description: " + description);
        print("Number of file changes: " + str(len(file_changes)));
        
        return transaction;
    }

    # Validate all changes in a transaction
    def validate_transaction(transaction: dict) -> dict {
        transaction_id = transaction["id"];
        changes = transaction["changes"];
        
        print("Validating transaction: " + transaction_id);
        
        validation_results = {
            "transaction_id": transaction_id,
            "total_changes": len(changes),
            "valid_changes": 0,
            "invalid_changes": 0,
            "validation_errors": [],
            "overall_valid": true
        };
        
        # Validate each change
        i = 0;
        while i < len(changes) {
            change = changes[i];
            validation = self.validate_single_change(change, i);
            
            if validation["valid"] {
                validation_results["valid_changes"] = validation_results["valid_changes"] + 1;
            } else {
                validation_results["invalid_changes"] = validation_results["invalid_changes"] + 1;
                validation_results["validation_errors"].append(validation["error"]);
                validation_results["overall_valid"] = false;
            }
            
            i = i + 1;
        }
        
        # Update transaction status
        if validation_results["overall_valid"] {
            transaction["validation_status"] = "valid";
            transaction["status"] = "validated";
            print("Transaction validation passed");
        } else {
            transaction["validation_status"] = "invalid";
            transaction["status"] = "validation_failed";
            print("Transaction validation failed with " + 
                  str(validation_results["invalid_changes"]) + " errors");
        }
        
        return validation_results;
    }

    # Validate a single change
    def validate_single_change(change: dict, index: int) -> dict {
        # Basic validation checks
        if not change.get("file_path") {
            return {"valid": false, "error": "Missing file_path in change " + str(index)};
        }
        
        if not change.get("content") {
            return {"valid": false, "error": "Missing content in change " + str(index)};
        }
        
        file_path = change["file_path"];
        content = change["content"];
        
        # File path validation
        if len(file_path) == 0 {
            return {"valid": false, "error": "Empty file path in change " + str(index)};
        }
        
        # Content validation
        if len(content) > 50000 {
            return {"valid": false, "error": "Content too large in change " + str(index)};
        }
        
        # File type validation
        if not self.is_supported_file_type(file_path) {
            return {"valid": false, "error": "Unsupported file type in change " + str(index) + ": " + file_path};
        }
        
        return {"valid": true, "error": ""};
    }

    # Check if file type is supported
    def is_supported_file_type(file_path: str) -> bool {
        supported_extensions = [".py", ".jac", ".js", ".json", ".md", ".txt", ".yaml", ".yml"];
        
        i = 0;
        while i < len(supported_extensions) {
            if supported_extensions[i] in file_path {
                return true;
            }
            i = i + 1;
        }
        
        return false;
    }

    # Order changes to minimize conflicts
    def order_changes(transaction: dict) -> dict {
        changes = transaction["changes"];
        print("Ordering " + str(len(changes)) + " changes to minimize conflicts");
        
        # Simple ordering strategy: sort by file path and priority
        ordered_changes = self.sort_changes_by_priority(changes);
        
        transaction["changes"] = ordered_changes;
        transaction["status"] = "ordered";
        
        print("Changes ordered successfully");
        return transaction;
    }

    # Sort changes by priority (files with dependencies first)
    def sort_changes_by_priority(changes: list) -> list {
        # Create priority scores
        scored_changes = [];
        i = 0;
        while i < len(changes) {
            change = changes[i];
            priority_score = self.calculate_change_priority(change);
            scored_change = {
                "change": change,
                "priority": priority_score
            };
            scored_changes.append(scored_change);
            i = i + 1;
        }
        
        # Sort by priority (higher priority first)
        sorted_scored = self.bubble_sort_by_priority(scored_changes);
        
        # Extract sorted changes
        sorted_changes = [];
        j = 0;
        while j < len(sorted_scored) {
            sorted_changes.append(sorted_scored[j]["change"]);
            j = j + 1;
        }
        
        return sorted_changes;
    }

    # Calculate priority for a change
    def calculate_change_priority(change: dict) -> float {
        file_path = change["file_path"];
        priority = 0.0;
        
        # Base files get highest priority
        if "main" in file_path or "init" in file_path {
            priority = priority + 1.0;
        }
        
        # Configuration files get high priority
        if "config" in file_path or "settings" in file_path {
            priority = priority + 0.8;
        }
        
        # Utility files get medium priority
        if "util" in file_path or "helper" in file_path {
            priority = priority + 0.6;
        }
        
        # Test files get lower priority
        if "test" in file_path {
            priority = priority + 0.3;
        }
        
        # Documentation gets lowest priority
        if ".md" in file_path or "doc" in file_path {
            priority = priority + 0.1;
        }
        
        return priority;
    }

    # Bubble sort implementation for priority sorting
    def bubble_sort_by_priority(items: list) -> list {
        n = len(items);
        sorted_items = items;  # Work with copy
        
        i = 0;
        while i < n - 1 {
            j = 0;
            while j < n - i - 1 {
                if sorted_items[j]["priority"] < sorted_items[j + 1]["priority"] {
                    temp = sorted_items[j];
                    sorted_items[j] = sorted_items[j + 1];
                    sorted_items[j + 1] = temp;
                }
                j = j + 1;
            }
            i = i + 1;
        }
        
        return sorted_items;
    }

    # Apply all changes in the transaction
    def apply_transaction(transaction: dict) -> dict {
        if transaction["status"] != "ordered" and transaction["status"] != "validated" {
            print("Error: Transaction must be validated and ordered before applying");
            return {"success": false, "error": "Invalid transaction status"};
        }
        
        transaction_id = transaction["id"];
        changes = transaction["changes"];
        
        print("Applying transaction: " + transaction_id);
        print("Applying " + str(len(changes)) + " changes...");
        
        apply_results = {
            "transaction_id": transaction_id,
            "total_changes": len(changes),
            "successful_changes": 0,
            "failed_changes": 0,
            "errors": []
        };
        
        # Apply each change
        i = 0;
        while i < len(changes) {
            change = changes[i];
            success = self.apply_single_change(change, i);
            
            if success {
                apply_results["successful_changes"] = apply_results["successful_changes"] + 1;
                print("Applied change " + str(i + 1) + ": " + change["file_path"]);
            } else {
                apply_results["failed_changes"] = apply_results["failed_changes"] + 1;
                error_msg = "Failed to apply change " + str(i + 1) + ": " + change["file_path"];
                apply_results["errors"].append(error_msg);
                print(error_msg);
            }
            
            i = i + 1;
        }
        
        # Update transaction status
        if apply_results["failed_changes"] == 0 {
            transaction["status"] = "applied";
            transaction["rollback_available"] = true;
            print("All changes applied successfully");
        } else {
            transaction["status"] = "partially_applied";
            transaction["rollback_available"] = true;
            print("Transaction partially applied with " + str(apply_results["failed_changes"]) + " failures");
        }
        
        return apply_results;
    }

    # Apply a single change (simulation)
    def apply_single_change(change: dict, index: int) -> bool {
        file_path = change["file_path"];
        content = change["content"];
        
        # Simulate file writing
        if "error" in content.lower() {
            return false;  # Simulate failure for content containing "error"
        }
        
        if len(content) == 0 {
            return false;  # Fail for empty content
        }
        
        return true;  # Simulate successful application
    }

    # Rollback a transaction
    def rollback_transaction(transaction: dict) -> dict {
        if not transaction["rollback_available"] {
            return {"success": false, "error": "Rollback not available for this transaction"};
        }
        
        transaction_id = transaction["id"];
        changes = transaction["changes"];
        
        print("Rolling back transaction: " + transaction_id);
        
        rollback_results = {
            "transaction_id": transaction_id,
            "total_changes": len(changes),
            "rollback_successful": 0,
            "rollback_failed": 0
        };
        
        # Rollback in reverse order
        i = len(changes) - 1;
        while i >= 0 {
            change = changes[i];
            success = self.rollback_single_change(change);
            
            if success {
                rollback_results["rollback_successful"] = rollback_results["rollback_successful"] + 1;
            } else {
                rollback_results["rollback_failed"] = rollback_results["rollback_failed"] + 1;
            }
            
            i = i - 1;
        }
        
        transaction["status"] = "rolled_back";
        transaction["rollback_available"] = false;
        
        print("Rollback completed - Successful: " + str(rollback_results["rollback_successful"]) + 
              ", Failed: " + str(rollback_results["rollback_failed"]));
        
        return rollback_results;
    }

    # Rollback a single change (simulation)
    def rollback_single_change(change: dict) -> bool {
        file_path = change["file_path"];
        print("Rolling back: " + file_path);
        return true;  # Simulate successful rollback
    }

    # Get transaction summary
    def get_transaction_summary(transaction: dict) -> str {
        summary = "TRANSACTION SUMMARY\n";
        summary = summary + "ID: " + transaction["id"] + "\n";
        summary = summary + "Description: " + transaction["description"] + "\n";
        summary = summary + "Status: " + transaction["status"] + "\n";
        summary = summary + "Total Files: " + str(transaction["total_files"]) + "\n";
        summary = summary + "Validation: " + transaction["validation_status"] + "\n";
        summary = summary + "Rollback Available: " + str(transaction["rollback_available"]);
        
        return summary;
    }

}
