from typing import Dict, Any, List

class ExplainableAIModule:
    @staticmethod
    def generate_grading_breakdown(
        evaluation_results: List[Dict[str, Any]], 
        custom_settings: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Aggregates evaluations and details the AI decision pathway, highlighting confidence and anomalies.
        """
        total_confidence = 0.0
        diagrams_count = 0
        formulas_count = 0
        total_questions = len(evaluation_results)

        for res in evaluation_results:
            total_confidence += res.get("confidence_score", 1.0)
            if res.get("diagram_detected", False):
                diagrams_count += 1
            if res.get("formula_detected", False):
                formulas_count += 1

        avg_confidence = total_confidence / total_questions if total_questions > 0 else 1.0
        
        # Configure breakdown percentages based on settings
        grammar_pct = 10.0
        if custom_settings:
            grammar_pct = custom_settings.get("grammar_weight", 0.1) * 100
            
        semantic_pct = (100.0 - grammar_pct) * 0.6
        keyword_pct = (100.0 - grammar_pct) * 0.4

        metrics = {
            "overall_confidence": round(avg_confidence, 2),
            "diagrams_found": diagrams_count,
            "formulas_found": formulas_count,
            "decision_factors": {
                "semantic_matching_weight": f"{round(semantic_pct, 1)}%",
                "keyword_density_weight": f"{round(keyword_pct, 1)}%",
                "grammar_deduction_weight": f"{round(grammar_pct, 1)}%"
            },
            "suggestions": []
        }

        # Generate structural alerts
        if avg_confidence < 0.75:
            metrics["suggestions"].append("Low confidence scores flagged. Hand-written style or low-resolution scan may have caused character segmentation drops. Please review.")
        if diagrams_count == 0:
            metrics["suggestions"].append("No architectural drawings or flow diagrams detected. Remind the student to structure descriptive processes visually.")
        else:
            metrics["suggestions"].append(f"Successfully identified {diagrams_count} diagram sketches, matching structural requirements.")
            
        return metrics
