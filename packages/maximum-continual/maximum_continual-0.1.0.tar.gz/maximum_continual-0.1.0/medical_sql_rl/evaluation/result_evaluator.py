"""
Result evaluation system for medical SQL RL environment.

Provides multiple evaluation strategies for comparing agent query results
against ground truth data with different tolerance levels and matching criteria.
"""

import math
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from datetime import datetime, date
import json


class ResultEvaluator:
    """Evaluates agent query results against ground truth with various strategies"""
    
    def __init__(self):
        self.evaluation_methods = {
            "exact_match": self._exact_match_score,
            "numerical_tolerance": self._numerical_tolerance_score,
            "set_match": self._set_match_score,
            "partial_match": self._partial_match_score,
            "semantic_match": self._semantic_match_score,
            "temporal_tolerance": self._temporal_tolerance_score
        }
    
    def evaluate_result(self, 
                       agent_result: List[Dict[str, Any]], 
                       ground_truth: List[Dict[str, Any]],
                       evaluation_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate agent results against ground truth
        
        Args:
            agent_result: Results returned by agent's SQL query
            ground_truth: Expected correct results
            evaluation_config: Configuration specifying evaluation method and parameters
            
        Returns:
            Dictionary with evaluation scores and details
        """
        eval_type = evaluation_config.get("evaluation_type", "exact_match")
        
        if eval_type not in self.evaluation_methods:
            return {
                "score": 0.0,
                "evaluation_type": eval_type,
                "error": f"Unknown evaluation type: {eval_type}",
                "details": {}
            }
        
        try:
            evaluation_method = self.evaluation_methods[eval_type]
            score, details = evaluation_method(agent_result, ground_truth, evaluation_config)
            
            return {
                "score": score,
                "evaluation_type": eval_type,
                "details": details,
                "agent_result_count": len(agent_result) if agent_result else 0,
                "ground_truth_count": len(ground_truth) if ground_truth else 0
            }
            
        except Exception as e:
            return {
                "score": 0.0,
                "evaluation_type": eval_type,
                "error": str(e),
                "details": {},
                "agent_result_count": len(agent_result) if agent_result else 0,
                "ground_truth_count": len(ground_truth) if ground_truth else 0
            }
    
    def _exact_match_score(self, 
                          agent_result: List[Dict], 
                          ground_truth: List[Dict], 
                          config: Dict) -> Tuple[float, Dict]:
        """Perfect match required for all fields and records"""
        if not ground_truth and not agent_result:
            return 1.0, {"match_type": "both_empty"}
        
        if len(agent_result) != len(ground_truth):
            return 0.0, {
                "match_type": "count_mismatch",
                "agent_count": len(agent_result),
                "expected_count": len(ground_truth)
            }
        
        # Sort both results for consistent comparison
        try:
            sorted_agent = sorted(agent_result, key=lambda x: json.dumps(x, sort_keys=True, default=str))
            sorted_ground_truth = sorted(ground_truth, key=lambda x: json.dumps(x, sort_keys=True, default=str))
        except Exception:
            # If sorting fails, compare as-is
            sorted_agent = agent_result
            sorted_ground_truth = ground_truth
        
        matches = 0
        mismatches = []
        
        for i, (agent_row, truth_row) in enumerate(zip(sorted_agent, sorted_ground_truth)):
            if self._normalize_row(agent_row) == self._normalize_row(truth_row):
                matches += 1
            else:
                mismatches.append({
                    "row_index": i,
                    "agent_row": agent_row,
                    "expected_row": truth_row,
                    "differences": self._find_row_differences(agent_row, truth_row)
                })
        
        score = matches / len(ground_truth) if ground_truth else 0.0
        
        return score, {
            "match_type": "exact",
            "matches": matches,
            "total_rows": len(ground_truth),
            "mismatches": mismatches[:5]  # Limit to first 5 mismatches
        }
    
    def _numerical_tolerance_score(self, 
                                  agent_result: List[Dict], 
                                  ground_truth: List[Dict], 
                                  config: Dict) -> Tuple[float, Dict]:
        """Allow numerical differences within specified tolerance"""
        tolerance = config.get("tolerance", 0.01)  # Default 1% tolerance
        
        if len(agent_result) != len(ground_truth):
            return 0.0, {
                "match_type": "count_mismatch", 
                "agent_count": len(agent_result),
                "expected_count": len(ground_truth),
                "tolerance": tolerance
            }
        
        if not ground_truth:
            return 1.0 if not agent_result else 0.0, {"match_type": "both_empty"}
        
        total_fields = 0
        matching_fields = 0
        field_scores = {}
        
        for agent_row, truth_row in zip(agent_result, ground_truth):
            row_matches, row_total, row_details = self._compare_rows_with_tolerance(
                agent_row, truth_row, tolerance
            )
            matching_fields += row_matches
            total_fields += row_total
            
            for field, details in row_details.items():
                if field not in field_scores:
                    field_scores[field] = {"matches": 0, "total": 0, "avg_error": 0}
                field_scores[field]["matches"] += 1 if details["match"] else 0
                field_scores[field]["total"] += 1
                if "error_pct" in details:
                    field_scores[field]["avg_error"] += details["error_pct"]
        
        # Calculate average errors for numerical fields
        for field in field_scores:
            if field_scores[field]["total"] > 0:
                field_scores[field]["avg_error"] /= field_scores[field]["total"]
        
        score = matching_fields / total_fields if total_fields > 0 else 0.0
        
        return score, {
            "match_type": "numerical_tolerance",
            "tolerance": tolerance,
            "matching_fields": matching_fields,
            "total_fields": total_fields,
            "field_scores": field_scores
        }
    
    def _set_match_score(self, 
                        agent_result: List[Dict], 
                        ground_truth: List[Dict], 
                        config: Dict) -> Tuple[float, Dict]:
        """Order doesn't matter, but all items must match"""
        if not ground_truth and not agent_result:
            return 1.0, {"match_type": "both_empty"}
        
        if len(agent_result) != len(ground_truth):
            return 0.0, {
                "match_type": "count_mismatch",
                "agent_count": len(agent_result),
                "expected_count": len(ground_truth)
            }
        
        # Convert to sets of normalized tuples for comparison
        try:
            agent_set = set()
            truth_set = set()
            
            for row in agent_result:
                normalized = tuple(sorted(self._normalize_row(row).items()))
                agent_set.add(normalized)
            
            for row in ground_truth:
                normalized = tuple(sorted(self._normalize_row(row).items()))
                truth_set.add(normalized)
            
            matches = len(agent_set.intersection(truth_set))
            score = matches / len(truth_set) if truth_set else 0.0
            
            missing = truth_set - agent_set
            extra = agent_set - truth_set
            
            return score, {
                "match_type": "set_match",
                "matches": matches,
                "total_expected": len(truth_set),
                "missing_records": len(missing),
                "extra_records": len(extra),
                "missing_sample": list(missing)[:3],  # Sample of missing
                "extra_sample": list(extra)[:3]  # Sample of extra
            }
            
        except Exception as e:
            # Fallback to exact match if set comparison fails
            return self._exact_match_score(agent_result, ground_truth, config)
    
    def _partial_match_score(self, 
                           agent_result: List[Dict], 
                           ground_truth: List[Dict], 
                           config: Dict) -> Tuple[float, Dict]:
        """Calculate precision and recall for partial matches"""
        if not ground_truth and not agent_result:
            return 1.0, {"match_type": "both_empty"}
        
        if not ground_truth:
            return 0.0, {"match_type": "no_ground_truth"}
        
        if not agent_result:
            return 0.0, {"match_type": "no_agent_results"}
        
        # Calculate precision and recall
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        # Convert ground truth to comparable format
        truth_normalized = [self._normalize_row(row) for row in ground_truth]
        agent_normalized = [self._normalize_row(row) for row in agent_result]
        
        # Find true positives
        matched_truth_indices = set()
        matched_agent_indices = set()
        
        for i, agent_row in enumerate(agent_normalized):
            best_match_idx = -1
            best_match_score = 0
            
            for j, truth_row in enumerate(truth_normalized):
                if j in matched_truth_indices:
                    continue
                    
                similarity = self._calculate_row_similarity(agent_row, truth_row)
                if similarity > best_match_score and similarity > 0.8:  # 80% similarity threshold
                    best_match_score = similarity
                    best_match_idx = j
            
            if best_match_idx >= 0:
                true_positives += 1
                matched_truth_indices.add(best_match_idx)
                matched_agent_indices.add(i)
        
        false_positives = len(agent_result) - true_positives
        false_negatives = len(ground_truth) - true_positives
        
        precision = true_positives / len(agent_result) if agent_result else 0
        recall = true_positives / len(ground_truth) if ground_truth else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return f1_score, {
            "match_type": "partial_match",
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score
        }
    
    def _semantic_match_score(self, 
                            agent_result: List[Dict], 
                            ground_truth: List[Dict], 
                            config: Dict) -> Tuple[float, Dict]:
        """Match based on semantic equivalence (e.g., different but equivalent representations)"""
        # For now, this is similar to set_match but with more flexible comparison
        tolerance = config.get("semantic_tolerance", 0.9)
        
        if not ground_truth and not agent_result:
            return 1.0, {"match_type": "both_empty"}
        
        if not ground_truth or not agent_result:
            return 0.0, {"match_type": "missing_data"}
        
        # Use partial match with lower threshold for semantic similarity
        matches = 0
        total_comparisons = max(len(agent_result), len(ground_truth))
        
        agent_matched = [False] * len(agent_result)
        truth_matched = [False] * len(ground_truth)
        
        for i, agent_row in enumerate(agent_result):
            agent_normalized = self._normalize_row(agent_row)
            
            for j, truth_row in enumerate(ground_truth):
                if truth_matched[j]:
                    continue
                
                truth_normalized = self._normalize_row(truth_row)
                similarity = self._calculate_row_similarity(agent_normalized, truth_normalized)
                
                if similarity >= tolerance:
                    matches += 1
                    agent_matched[i] = True
                    truth_matched[j] = True
                    break
        
        score = matches / total_comparisons
        
        return score, {
            "match_type": "semantic_match",
            "matches": matches,
            "total_comparisons": total_comparisons,
            "semantic_tolerance": tolerance,
            "unmatched_agent": sum(1 for x in agent_matched if not x),
            "unmatched_truth": sum(1 for x in truth_matched if not x)
        }
    
    def _temporal_tolerance_score(self, 
                                agent_result: List[Dict], 
                                ground_truth: List[Dict], 
                                config: Dict) -> Tuple[float, Dict]:
        """Allow tolerance for date/time fields"""
        time_tolerance_days = config.get("time_tolerance_days", 1)
        
        # Use numerical tolerance approach but with special handling for dates
        if len(agent_result) != len(ground_truth):
            return 0.0, {
                "match_type": "count_mismatch",
                "time_tolerance_days": time_tolerance_days
            }
        
        total_fields = 0
        matching_fields = 0
        
        for agent_row, truth_row in zip(agent_result, ground_truth):
            for field in truth_row:
                if field not in agent_row:
                    total_fields += 1
                    continue
                
                agent_val = agent_row[field]
                truth_val = truth_row[field]
                
                total_fields += 1
                
                if self._are_temporal_values_close(agent_val, truth_val, time_tolerance_days):
                    matching_fields += 1
                elif self._normalize_value(agent_val) == self._normalize_value(truth_val):
                    matching_fields += 1
        
        score = matching_fields / total_fields if total_fields > 0 else 0.0
        
        return score, {
            "match_type": "temporal_tolerance",
            "time_tolerance_days": time_tolerance_days,
            "matching_fields": matching_fields,
            "total_fields": total_fields
        }
    
    def _normalize_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a row for comparison"""
        normalized = {}
        for key, value in row.items():
            normalized[key.lower()] = self._normalize_value(value)
        return normalized
    
    def _normalize_value(self, value: Any) -> Any:
        """Normalize a single value for comparison"""
        if value is None:
            return None
        elif isinstance(value, str):
            return value.strip().lower()
        elif isinstance(value, (int, float)):
            return float(value) if not math.isnan(float(value)) else None
        elif isinstance(value, (date, datetime)):
            return value.isoformat()
        else:
            return str(value).strip().lower()
    
    def _find_row_differences(self, agent_row: Dict, truth_row: Dict) -> List[Dict]:
        """Find specific differences between two rows"""
        differences = []
        
        all_keys = set(agent_row.keys()) | set(truth_row.keys())
        
        for key in all_keys:
            agent_val = agent_row.get(key)
            truth_val = truth_row.get(key)
            
            if self._normalize_value(agent_val) != self._normalize_value(truth_val):
                differences.append({
                    "field": key,
                    "agent_value": agent_val,
                    "expected_value": truth_val
                })
        
        return differences
    
    def _compare_rows_with_tolerance(self, 
                                   agent_row: Dict, 
                                   truth_row: Dict, 
                                   tolerance: float) -> Tuple[int, int, Dict]:
        """Compare two rows with numerical tolerance"""
        matches = 0
        total = 0
        field_details = {}
        
        all_keys = set(agent_row.keys()) | set(truth_row.keys())
        
        for key in all_keys:
            total += 1
            agent_val = agent_row.get(key)
            truth_val = truth_row.get(key)
            
            if agent_val is None and truth_val is None:
                matches += 1
                field_details[key] = {"match": True, "type": "both_null"}
            elif agent_val is None or truth_val is None:
                field_details[key] = {"match": False, "type": "null_mismatch"}
            elif isinstance(agent_val, (int, float)) and isinstance(truth_val, (int, float)):
                # Numerical comparison with tolerance
                if truth_val == 0:
                    error = abs(agent_val - truth_val)
                    within_tolerance = error <= tolerance
                else:
                    error_pct = abs(agent_val - truth_val) / abs(truth_val)
                    within_tolerance = error_pct <= tolerance
                
                if within_tolerance:
                    matches += 1
                
                field_details[key] = {
                    "match": within_tolerance,
                    "type": "numerical",
                    "error_pct": error_pct if truth_val != 0 else error,
                    "agent_val": agent_val,
                    "truth_val": truth_val
                }
            else:
                # String/other comparison
                match = self._normalize_value(agent_val) == self._normalize_value(truth_val)
                if match:
                    matches += 1
                
                field_details[key] = {
                    "match": match,
                    "type": "string",
                    "agent_val": agent_val,
                    "truth_val": truth_val
                }
        
        return matches, total, field_details
    
    def _calculate_row_similarity(self, row1: Dict, row2: Dict) -> float:
        """Calculate similarity score between two rows"""
        all_keys = set(row1.keys()) | set(row2.keys())
        if not all_keys:
            return 1.0
        
        matches = 0
        for key in all_keys:
            val1 = row1.get(key)
            val2 = row2.get(key)
            
            if val1 == val2:
                matches += 1
            elif isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numerical similarity
                if val2 != 0:
                    error = abs(val1 - val2) / abs(val2)
                    if error <= 0.1:  # 10% tolerance for similarity
                        matches += 0.8  # Partial credit
                else:
                    if abs(val1) <= 0.1:  # Close to zero
                        matches += 0.8
        
        return matches / len(all_keys)
    
    def _are_temporal_values_close(self, val1: Any, val2: Any, tolerance_days: int) -> bool:
        """Check if two temporal values are within tolerance"""
        try:
            # Try to parse as dates/datetimes
            date1 = self._parse_temporal_value(val1)
            date2 = self._parse_temporal_value(val2)
            
            if date1 and date2:
                diff = abs((date1 - date2).days)
                return diff <= tolerance_days
                
        except Exception:
            pass
        
        return False
    
    def _parse_temporal_value(self, value: Any) -> Optional[date]:
        """Parse various temporal value formats"""
        if isinstance(value, date):
            return value
        elif isinstance(value, datetime):
            return value.date()
        elif isinstance(value, str):
            # Try common date formats
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]:
                try:
                    parsed = datetime.strptime(value, fmt)
                    return parsed.date()
                except ValueError:
                    continue
        
        return None
