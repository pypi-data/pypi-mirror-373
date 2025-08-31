#!/usr/bin/env python
"""
Hybrid Statistical Analysis for 24-Hour paGLU Research

This script provides enhanced statistical analysis of existing results
and can incorporate new multi-seed data as it becomes available.
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Hybrid statistical analysis")
    
    parser.add_argument("--output_dir", type=str, default="analysis/hybrid_24h",
                        help="Directory to save analysis outputs")
    parser.add_argument("--update_interval", type=int, default=300,
                        help="Update interval in seconds for live results")
    
    return parser.parse_args()


class HybridStatisticalAnalyzer:
    """Hybrid statistical analysis combining existing and live results."""
    
    def __init__(self, args):
        self.args = args
        self.output_dir = Path(args.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing verified results
        self.existing_results = self._load_existing_results()
        
        # Analysis results
        self.analysis = {
            "existing": {},
            "live": {},
            "combined": {},
            "publication_readiness": {}
        }
    
    def _load_existing_results(self):
        """Load and parse existing verified results."""
        results = {
            "nlp": {
                "baseline_loss": 2.0247,
                "paglu_loss": 1.9865,
                "improvement_pct": 1.89,
                "n_seeds": 1,
                "source": "phase2_verified"
            },
            "vision": {
                "paglu_acc": 59.12,
                "ranking": 1,
                "n_seeds": 1,
                "source": "benchmark_verified"
            }
        }
        return results
    
    def analyze_existing_results(self):
        """Analyze existing results with enhanced statistical perspective."""
        print("📊 Analyzing existing verified results...")
        
        # NLP Analysis
        nlp = self.existing_results["nlp"]
        baseline_loss = nlp["baseline_loss"]
        paglu_loss = nlp["paglu_loss"]
        improvement = nlp["improvement_pct"]
        
        # Calculate effect size (estimated)
        estimated_std = 0.1  # Conservative estimate based on typical NLP variance
        cohens_d = (baseline_loss - paglu_loss) / estimated_std
        
        self.analysis["existing"]["nlp"] = {
            "baseline_loss": baseline_loss,
            "paglu_loss": paglu_loss,
            "improvement_pct": improvement,
            "estimated_cohens_d": cohens_d,
            "effect_size": self._interpret_effect_size(abs(cohens_d)),
            "practical_significance": improvement > 1.0,  # >1% is meaningful in NLP
            "n_seeds": 1,
            "confidence": "high_single_seed"
        }
        
        # Vision Analysis
        vision = self.existing_results["vision"]
        paglu_acc = vision["paglu_acc"]
        
        self.analysis["existing"]["vision"] = {
            "paglu_acc": paglu_acc,
            "ranking": 1,
            "competitive_advantage": paglu_acc > 58.0,  # Above typical CIFAR-10 baselines
            "n_seeds": 1,
            "confidence": "high_single_seed"
        }
        
        print(f"✅ NLP: {improvement:.2f}% improvement (Cohen's d ≈ {cohens_d:.2f})")
        print(f"✅ Vision: {paglu_acc:.2f}% accuracy (#1 ranking)")
    
    def check_live_results(self):
        """Check for new experimental results."""
        live_results_path = Path("experiments/hybrid_24h/expedited_results.json")
        
        if live_results_path.exists():
            try:
                with open(live_results_path, 'r') as f:
                    data = json.load(f)
                
                live_results = data.get("results", {})
                
                # Process NLP results
                nlp_results = live_results.get("nlp", [])
                if nlp_results:
                    self._process_live_nlp_results(nlp_results)
                
                # Process vision results
                vision_results = live_results.get("vision", [])
                if vision_results:
                    self._process_live_vision_results(vision_results)
                
                return True
            except Exception as e:
                print(f"⚠️ Error reading live results: {e}")
                return False
        else:
            print("⏳ Waiting for live experimental results...")
            return False
    
    def _process_live_nlp_results(self, nlp_results):
        """Process live NLP experimental results."""
        baseline_losses = []
        paglu_losses = []
        
        for result in nlp_results:
            if result["status"] == "success" and "eval_loss" in result["results"]:
                config = result["config"]
                eval_loss = result["results"]["eval_loss"]
                
                if config["alpha"] == 0.0:  # Baseline
                    baseline_losses.append(eval_loss)
                elif config["alpha"] == 0.5:  # paGLU
                    paglu_losses.append(eval_loss)
        
        if len(baseline_losses) >= 2 and len(paglu_losses) >= 2:
            # Multi-seed statistical analysis
            baseline_mean = np.mean(baseline_losses)
            paglu_mean = np.mean(paglu_losses)
            
            # Statistical tests
            t_stat, p_value = stats.ttest_ind(baseline_losses, paglu_losses)
            
            # Effect size
            pooled_std = np.sqrt((np.var(baseline_losses, ddof=1) + np.var(paglu_losses, ddof=1)) / 2)
            cohens_d = (baseline_mean - paglu_mean) / pooled_std
            
            improvement = ((baseline_mean - paglu_mean) / baseline_mean) * 100
            
            self.analysis["live"]["nlp"] = {
                "baseline_mean": baseline_mean,
                "baseline_std": np.std(baseline_losses, ddof=1),
                "paglu_mean": paglu_mean,
                "paglu_std": np.std(paglu_losses, ddof=1),
                "improvement_pct": improvement,
                "t_statistic": t_stat,
                "p_value": p_value,
                "cohens_d": cohens_d,
                "effect_size": self._interpret_effect_size(abs(cohens_d)),
                "is_significant": p_value < 0.05,
                "n_baseline": len(baseline_losses),
                "n_paglu": len(paglu_losses),
                "confidence": "multi_seed_validated"
            }
            
            print(f"🔥 LIVE NLP: {improvement:.2f}% improvement (p={p_value:.4f})")
    
    def _process_live_vision_results(self, vision_results):
        """Process live vision experimental results."""
        paglu_accs = []
        relu_accs = []
        gelu_accs = []
        
        for result in vision_results:
            if result["status"] == "success" and "test_acc" in result["results"]:
                config = result["config"]
                test_acc = result["results"]["test_acc"]
                
                if config["unit"] == "paGLU":
                    paglu_accs.append(test_acc)
                elif config["unit"] == "ReLU":
                    relu_accs.append(test_acc)
                elif config["unit"] == "GELU":
                    gelu_accs.append(test_acc)
        
        if len(paglu_accs) >= 2:
            paglu_mean = np.mean(paglu_accs)
            
            comparisons = {}
            
            # Compare with ReLU if available
            if len(relu_accs) >= 2:
                relu_mean = np.mean(relu_accs)
                t_stat, p_value = stats.ttest_ind(paglu_accs, relu_accs)
                
                pooled_std = np.sqrt((np.var(paglu_accs, ddof=1) + np.var(relu_accs, ddof=1)) / 2)
                cohens_d = (paglu_mean - relu_mean) / pooled_std
                improvement = ((paglu_mean - relu_mean) / relu_mean) * 100
                
                comparisons["vs_ReLU"] = {
                    "improvement_pct": improvement,
                    "p_value": p_value,
                    "cohens_d": cohens_d,
                    "is_significant": p_value < 0.05
                }
            
            self.analysis["live"]["vision"] = {
                "paglu_mean": paglu_mean,
                "paglu_std": np.std(paglu_accs, ddof=1),
                "n_seeds": len(paglu_accs),
                "comparisons": comparisons,
                "confidence": "multi_seed_validated"
            }
            
            print(f"🔥 LIVE Vision: {paglu_mean:.2f}% accuracy")
    
    def _interpret_effect_size(self, d):
        """Interpret Cohen's d effect size."""
        if d < 0.2:
            return "negligible"
        elif d < 0.5:
            return "small"
        elif d < 0.8:
            return "medium"
        else:
            return "large"
    
    def assess_publication_readiness(self):
        """Assess current publication readiness."""
        score = 0
        criteria = []
        
        # Existing results (4 points)
        existing_nlp = self.analysis.get("existing", {}).get("nlp", {})
        existing_vision = self.analysis.get("existing", {}).get("vision", {})
        
        if existing_nlp:
            score += 2
            criteria.append("✅ Verified NLP improvement (1.89%)")
        
        if existing_vision:
            score += 2
            criteria.append("✅ Verified vision performance (59.12%)")
        
        # Multi-seed validation (3 points)
        live_nlp = self.analysis.get("live", {}).get("nlp", {})
        live_vision = self.analysis.get("live", {}).get("vision", {})
        
        if live_nlp and live_nlp.get("n_baseline", 0) >= 2:
            score += 2
            criteria.append("✅ NLP multi-seed validation")
        else:
            criteria.append("❌ NLP multi-seed validation")
        
        if live_vision and live_vision.get("n_seeds", 0) >= 2:
            score += 1
            criteria.append("✅ Vision multi-seed validation")
        else:
            criteria.append("❌ Vision multi-seed validation")
        
        # Statistical significance (3 points)
        if live_nlp and live_nlp.get("is_significant"):
            score += 2
            criteria.append("✅ NLP statistical significance")
        else:
            criteria.append("❌ NLP statistical significance")
        
        if live_vision and live_vision.get("comparisons", {}).get("vs_ReLU", {}).get("is_significant"):
            score += 1
            criteria.append("✅ Vision statistical significance")
        else:
            criteria.append("❌ Vision statistical significance")
        
        self.analysis["publication_readiness"] = {
            "score": score,
            "max_score": 10,
            "criteria": criteria,
            "readiness_level": self._get_readiness_level(score)
        }
        
        return score
    
    def _get_readiness_level(self, score):
        """Get readiness level based on score."""
        if score >= 8:
            return "READY FOR PUBLICATION"
        elif score >= 6:
            return "CONDITIONALLY READY"
        else:
            return "NEEDS MORE VALIDATION"
    
    def generate_live_report(self):
        """Generate live publication readiness report."""
        report_lines = []
        
        report_lines.append("# Hybrid Statistical Analysis - Live Report")
        report_lines.append(f"## paGLU 24-Hour Publication Readiness")
        report_lines.append("")
        report_lines.append(f"**Analysis Time:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Current readiness
        readiness = self.analysis["publication_readiness"]
        report_lines.append("## Current Publication Readiness")
        report_lines.append("")
        report_lines.append(f"**Score: {readiness['score']}/10**")
        report_lines.append(f"**Status: {readiness['readiness_level']}**")
        report_lines.append("")
        
        for criterion in readiness["criteria"]:
            report_lines.append(f"- {criterion}")
        
        report_lines.append("")
        
        # Existing results
        existing_nlp = self.analysis.get("existing", {}).get("nlp", {})
        if existing_nlp:
            report_lines.append("### Verified NLP Results")
            report_lines.append(f"- **Improvement:** {existing_nlp['improvement_pct']:.2f}%")
            report_lines.append(f"- **Effect Size:** {existing_nlp['effect_size']} (d ≈ {existing_nlp['estimated_cohens_d']:.2f})")
            report_lines.append(f"- **Practical Significance:** {'Yes' if existing_nlp['practical_significance'] else 'No'}")
            report_lines.append("")
        
        # Live results
        live_nlp = self.analysis.get("live", {}).get("nlp", {})
        if live_nlp:
            report_lines.append("### Live NLP Validation")
            report_lines.append(f"- **Multi-seed Improvement:** {live_nlp['improvement_pct']:.2f}%")
            report_lines.append(f"- **Statistical Significance:** p = {live_nlp['p_value']:.4f}")
            report_lines.append(f"- **Effect Size:** {live_nlp['effect_size']} (d = {live_nlp['cohens_d']:.3f})")
            report_lines.append(f"- **Seeds:** {live_nlp['n_baseline']} baseline, {live_nlp['n_paglu']} paGLU")
            report_lines.append("")
        
        # Save report
        report_file = self.output_dir / "live_readiness_report.md"
        with open(report_file, 'w') as f:
            f.write('\n'.join(report_lines))
        
        # Save analysis data
        analysis_file = self.output_dir / "live_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(self.analysis, f, indent=2, default=str)
        
        return readiness["score"]
    
    def run_hybrid_analysis(self):
        """Run the complete hybrid analysis."""
        print("🔬 Hybrid Statistical Analysis - Live Tracking")
        print("=" * 60)
        
        # Always analyze existing results
        self.analyze_existing_results()
        
        # Check for live results
        has_live = self.check_live_results()
        
        # Assess readiness
        score = self.assess_publication_readiness()
        
        # Generate report
        self.generate_live_report()
        
        print("=" * 60)
        print(f"📊 Current Publication Readiness: {score}/10")
        
        if score >= 8:
            print("🟢 READY FOR PUBLICATION!")
        elif score >= 6:
            print("🟡 CONDITIONALLY READY - Close to target!")
        else:
            print("🔴 NEEDS MORE VALIDATION - Experiments in progress...")
        
        return self.analysis, score


def main():
    """Main execution function."""
    args = parse_args()
    
    analyzer = HybridStatisticalAnalyzer(args)
    analysis, score = analyzer.run_hybrid_analysis()
    
    return analysis, score


if __name__ == "__main__":
    main() 