# impact_analyzer_syntax.jac
# Impact analyzer - Syntax-corrected version
# Analyzes the impact of proposed changes across the codebase

# Node definitions
node ImpactReport {}
node FileImpact {}
node DependencyImpact {}

walker ImpactAnalyzer {

    # Analyze impact of proposed changes
    def analyze_change_impact(change_description: str, affected_files: list) -> dict {
        print("Analyzing impact for: " + change_description);
        print("Affected files: " + str(len(affected_files)));
        
        impact_report = {
            "change_id": "impact_" + str(len(affected_files)),
            "description": change_description,
            "affected_files": affected_files,
            "impact_score": 0.0,
            "risk_level": "low",
            "dependencies": [],
            "recommendations": []
        };
        
        # Calculate overall impact score
        total_impact = 0.0;
        i = 0;
        while i < len(affected_files) {
            file_impact = self.calculate_file_impact(affected_files[i]);
            total_impact = total_impact + file_impact;
            i = i + 1;
        }
        
        impact_report["impact_score"] = total_impact;
        impact_report["risk_level"] = self.determine_risk_level(total_impact);
        impact_report["dependencies"] = self.find_dependencies(affected_files);
        impact_report["recommendations"] = self.generate_recommendations(impact_report);
        
        return impact_report;
    }

    # Calculate impact score for a single file
    def calculate_file_impact(file_path: str) -> float {
        impact_score = 0.0;
        
        # Base impact based on file type and location
        if "main" in file_path or "__init__" in file_path {
            impact_score = impact_score + 2.0;  # High impact for main files
        } elif "config" in file_path or "settings" in file_path {
            impact_score = impact_score + 1.5;  # Medium-high for config
        } elif "util" in file_path or "helper" in file_path {
            impact_score = impact_score + 1.0;  # Medium for utilities
        } elif "test" in file_path {
            impact_score = impact_score + 0.5;  # Lower for tests
        } else {
            impact_score = impact_score + 0.8;  # Default impact
        }
        
        # Additional impact based on file extension
        if ".py" in file_path {
            impact_score = impact_score + 0.3;
        } elif ".jac" in file_path {
            impact_score = impact_score + 0.5;  # Jac files might be more critical
        } elif ".js" in file_path {
            impact_score = impact_score + 0.3;
        } elif ".json" in file_path or ".yaml" in file_path {
            impact_score = impact_score + 0.4;  # Config files
        }
        
        return impact_score;
    }

    # Determine risk level based on impact score
    def determine_risk_level(impact_score: float) -> str {
        if impact_score >= 5.0 {
            return "critical";
        } elif impact_score >= 3.0 {
            return "high";
        } elif impact_score >= 1.5 {
            return "medium";
        } else {
            return "low";
        }
    }

    # Find dependencies between files
    def find_dependencies(files: list) -> list {
        dependencies = [];
        
        i = 0;
        while i < len(files) {
            file_path = files[i];
            
            # Simulate dependency detection based on file patterns
            if "main" in file_path {
                # Main files typically depend on many others
                j = 0;
                while j < len(files) {
                    if j != i and not ("main" in files[j]) {
                        dependency = {
                            "from": file_path,
                            "to": files[j],
                            "type": "imports"
                        };
                        dependencies.append(dependency);
                    }
                    j = j + 1;
                }
            } elif "config" in file_path {
                # Config files are often imported by others
                dependency = {
                    "from": "multiple_files",
                    "to": file_path,
                    "type": "configuration"
                };
                dependencies.append(dependency);
            }
            
            i = i + 1;
        }
        
        return dependencies;
    }

    # Generate recommendations based on impact analysis
    def generate_recommendations(impact_report: dict) -> list {
        recommendations = [];
        risk_level = impact_report["risk_level"];
        affected_files = impact_report["affected_files"];
        
        if risk_level == "critical" {
            recommendations.append("Require multiple reviewers for this change");
            recommendations.append("Implement comprehensive testing before deployment");
            recommendations.append("Consider rolling out in stages");
        } elif risk_level == "high" {
            recommendations.append("Ensure thorough testing of affected components");
            recommendations.append("Review impact on dependent modules");
            recommendations.append("Consider backup/rollback strategy");
        } elif risk_level == "medium" {
            recommendations.append("Run automated tests for affected areas");
            recommendations.append("Review changes with team lead");
        } else {
            recommendations.append("Standard review process should be sufficient");
        }
        
        # File-specific recommendations
        i = 0;
        while i < len(affected_files) {
            file_path = affected_files[i];
            if "test" in file_path {
                recommendations.append("Update related test files if necessary");
            } elif "config" in file_path {
                recommendations.append("Verify configuration changes in staging environment");
            } elif "main" in file_path {
                recommendations.append("Test main application flow thoroughly");
            }
            i = i + 1;
        }
        
        return recommendations;
    }

    # Estimate impact on performance
    def estimate_performance_impact(files: list, change_type: str) -> dict {
        performance_impact = {
            "affected_areas": [],
            "performance_risk": "low",
            "estimated_impact": 0.0
        };
        
        # Analyze performance impact based on change type
        if change_type == "algorithm_change" {
            performance_impact["performance_risk"] = "high";
            performance_impact["estimated_impact"] = 2.5;
        } elif change_type == "database_change" {
            performance_impact["performance_risk"] = "medium";
            performance_impact["estimated_impact"] = 1.8;
        } elif change_type == "ui_change" {
            performance_impact["performance_risk"] = "low";
            performance_impact["estimated_impact"] = 0.5;
        } else {
            performance_impact["estimated_impact"] = 1.0;
        }
        
        # Check for performance-sensitive files
        i = 0;
        while i < len(files) {
            file_path = files[i];
            if "algorithm" in file_path or "compute" in file_path {
                performance_impact["affected_areas"].append("computational_performance");
            } elif "db" in file_path or "database" in file_path {
                performance_impact["affected_areas"].append("database_performance");
            } elif "api" in file_path or "endpoint" in file_path {
                performance_impact["affected_areas"].append("api_performance");
            }
            i = i + 1;
        }
        
        return performance_impact;
    }

    # Generate impact visualization data
    def generate_impact_visualization(impact_report: dict) -> dict {
        visualization = {
            "impact_score": impact_report["impact_score"],
            "risk_level": impact_report["risk_level"],
            "file_count": len(impact_report["affected_files"]),
            "dependency_count": len(impact_report["dependencies"]),
            "chart_data": []
        };
        
        # Create chart data for visualization
        files = impact_report["affected_files"];
        i = 0;
        while i < len(files) {
            file_impact = self.calculate_file_impact(files[i]);
            chart_point = {
                "file": files[i],
                "impact": file_impact,
                "category": self.categorize_file(files[i])
            };
            visualization["chart_data"].append(chart_point);
            i = i + 1;
        }
        
        return visualization;
    }

    # Categorize file by type
    def categorize_file(file_path: str) -> str {
        if "main" in file_path {
            return "core";
        } elif "config" in file_path {
            return "configuration";
        } elif "test" in file_path {
            return "testing";
        } elif "util" in file_path or "helper" in file_path {
            return "utility";
        } elif "api" in file_path or "endpoint" in file_path {
            return "api";
        } else {
            return "other";
        }
    }

    # Generate impact summary report
    def generate_impact_summary(impact_report: dict) -> str {
        summary = "IMPACT ANALYSIS SUMMARY\n";
        summary = summary + "======================\n";
        summary = summary + "Change: " + impact_report["description"] + "\n";
        summary = summary + "Risk Level: " + impact_report["risk_level"] + "\n";
        summary = summary + "Impact Score: " + str(impact_report["impact_score"]) + "\n";
        summary = summary + "Files Affected: " + str(len(impact_report["affected_files"])) + "\n";
        summary = summary + "Dependencies: " + str(len(impact_report["dependencies"])) + "\n";
        summary = summary + "\nRecommendations:\n";
        
        recommendations = impact_report["recommendations"];
        i = 0;
        while i < len(recommendations) {
            summary = summary + "- " + recommendations[i] + "\n";
            i = i + 1;
        }
        
        return summary;
    }

}
