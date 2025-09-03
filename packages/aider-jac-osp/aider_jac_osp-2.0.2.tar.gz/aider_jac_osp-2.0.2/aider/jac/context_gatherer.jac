# context_gatherer_syntax.jac
# Smart context collection utilities - Syntax-corrected version
# Collects the most relevant nodes/files from the RepoMap for a given query or task.

walker ContextGatherer {

    # Main method to gather context based on query
    def gather_context(query: str, max_items: int) -> list {
        results = [];
        
        # Create mock candidates for demonstration
        candidates = [];
        i = 0;
        while i < 20 {
            candidates.append("file_" + str(i) + ".py");
            i = i + 1;
        }

        # Score and filter candidates
        scored_items = [];
        j = 0;
        while j < len(candidates) {
            score = self.calculate_relevance_score(candidates[j], query);
            if score > 0.5 {
                item = {
                    "file": candidates[j],
                    "score": score,
                    "tokens": self.estimate_tokens(candidates[j])
                };
                scored_items.append(item);
            }
            j = j + 1;
        }

        # Sort by score (simple bubble sort)
        sorted_items = self.sort_by_score(scored_items);
        
        # Select top items within budget
        selected = [];
        total_tokens = 0;
        token_budget = 2048;
        k = 0;
        while k < len(sorted_items) and k < max_items {
            item_tokens = sorted_items[k]["tokens"];
            if total_tokens + item_tokens <= token_budget {
                selected.append(sorted_items[k]["file"]);
                total_tokens = total_tokens + item_tokens;
            }
            k = k + 1;
        }

        return selected;
    }

    # Calculate relevance score for a file
    def calculate_relevance_score(filename: str, query: str) -> float {
        score = 0.0;
        
        # Basic scoring based on filename content
        if query in filename {
            score = score + 1.0;
        }
        if "main" in filename {
            score = score + 0.5;
        }
        if "util" in filename {
            score = score + 0.3;
        }
        if "test" in filename {
            score = score + 0.2;
        }
        
        return score;
    }

    # Sort items by score (descending)
    def sort_by_score(items: list) -> list {
        n = len(items);
        sorted_items = items; # Work with copy
        
        # Bubble sort implementation
        i = 0;
        while i < n - 1 {
            j = 0;
            while j < n - i - 1 {
                if sorted_items[j]["score"] < sorted_items[j + 1]["score"] {
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

    # Estimate token count for content
    def estimate_tokens(content: str) -> int {
        # Simple estimation: 4 characters per token
        return len(content) * 25;  # Assume average file size multiplier
    }

    # Get summary of gathered context
    def get_context_summary(context_items: list) -> str {
        count = len(context_items);
        if count == 0 {
            return "No context items found";
        } elif count == 1 {
            return "Found 1 relevant item: " + context_items[0];
        } else {
            return "Found " + str(count) + " relevant items, including: " + 
                   context_items[0] + ", " + context_items[1];
        }
    }

    # Filter context by specific criteria
    def filter_context(items: list, criteria: str) -> list {
        filtered = [];
        i = 0;
        while i < len(items) {
            if criteria in items[i] {
                filtered.append(items[i]);
            }
            i = i + 1;
        }
        return filtered;
    }

    # Expand context with related files
    def expand_context(base_items: list) -> list {
        expanded = base_items;  # Start with base items
        
        # Add related files (simulation)
        i = 0;
        while i < len(base_items) {
            base_file = base_items[i];
            if ".py" in base_file {
                # Add potential test file
                test_file = base_file.replace(".py", "_test.py");
                expanded.append(test_file);
                # Add potential config file
                config_file = base_file.replace(".py", "_config.py");
                expanded.append(config_file);
            }
            i = i + 1;
        }
        
        return expanded;
    }

}
