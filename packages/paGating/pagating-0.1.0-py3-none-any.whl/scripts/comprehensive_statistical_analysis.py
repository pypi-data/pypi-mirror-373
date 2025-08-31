#!/usr/bin/env python
"""
Comprehensive Statistical Analysis for Multi-Seed paGLU Results

This script performs rigorous statistical analysis on multi-seed experimental results,
including proper t-tests, confidence intervals, effect sizes, and publication-ready reports.
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Comprehensive statistical analysis of multi-seed results")
    
    parser.add_argument("--results_file", type=str, required=True,
                        help="JSON file with multi-seed experimental results")
    parser.add_argument("--output_dir", type=str, default="analysis/comprehensive_stats",
                        help="Directory to save analysis outputs")
    parser.add_argument("--alpha", type=float, default=0.05,
                        help="Significance level for statistical tests")
    parser.add_argument("--confidence", type=float, default=0.95,
                        help="Confidence level for intervals")
    parser.add_argument("--min_seeds", type=int, default=3,
                        help="Minimum seeds required for statistical testing")
    
    return parser.parse_args()


class ComprehensiveStatisticalAnalyzer:
    """Comprehensive statistical analysis for multi-seed experiments."""
    
    def __init__(self, results_file, output_dir, alpha=0.05, confidence=0.95, min_seeds=3):
        self.results_file = Path(results_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.alpha = alpha
        self.confidence = confidence
        self.min_seeds = min_seeds
        
        # Load results
        with open(self.results_file, 'r') as f:
            self.data = json.load(f)
        
        self.metadata = self.data.get("metadata", {})
        self.results = self.data.get("results", {})
        
        # Analysis results
        self.analysis = {
            "nlp": {"experiments": {}, "comparisons": {}, "summary": {}},
            "vision": {"experiments": {}, "comparisons": {}, "summary": {}}
        }
    
    def analyze_domain_results(self, domain):
        """Analyze results for a specific domain (nlp or vision)."""
        domain_results = self.results.get(domain, [])
        
        if not domain_results:
            print(f"⚠️ No {domain.upper()} results found")
            return
        
        print(f"🔬 Analyzing {domain.upper()} results...")
        
        # Group results by configuration
        config_groups = {}
        for result in domain_results:
            if result["status"] != "success":
                continue
                
            config = result["config"]
            if domain == "nlp":
                key = f"{config['unit']}_alpha{config['alpha']}_lr{config['lr']}"
            else:
                key = f"{config['unit']}"
                if config.get('alpha') is not None:
                    key += f"_alpha{config['alpha']}"
            
            if key not in config_groups:
                config_groups[key] = []
            config_groups[key].append(result)
        
        # Analyze each configuration
        for config_name, results_list in config_groups.items():
            self.analyze_configuration(domain, config_name, results_list)
        
        # Perform pairwise comparisons
        self.perform_pairwise_comparisons(domain, config_groups)
        
        # Generate domain summary
        self.generate_domain_summary(domain, config_groups)
    
    def analyze_configuration(self, domain, config_name, results_list):
        """Analyze a single configuration across multiple seeds."""
        if len(results_list) < self.min_seeds:
            print(f"⚠️ {config_name}: Only {len(results_list)} seeds, need {self.min_seeds} for stats")
            return
        
        # Extract metrics
        if domain == "nlp":
            train_losses = [r["results"].get("train_loss") for r in results_list if r["results"].get("train_loss")]
            eval_losses = [r["results"].get("eval_loss") for r in results_list if r["results"].get("eval_loss")]
            
            metrics = {
                "train_loss": train_losses,
                "eval_loss": eval_losses
            }
        else:  # vision
            val_accs = [r["results"].get("val_acc") for r in results_list if r["results"].get("val_acc")]
            test_accs = [r["results"].get("test_acc") for r in results_list if r["results"].get("test_acc")]
            
            metrics = {
                "val_acc": val_accs,
                "test_acc": test_accs
            }
        
        # Calculate statistics for each metric
        config_stats = {}
        for metric_name, values in metrics.items():
            if not values or len(values) < self.min_seeds:
                continue
                
            values = np.array(values)
            
            # Basic statistics
            mean_val = np.mean(values)
            std_val = np.std(values, ddof=1)
            sem_val = stats.sem(values)
            
            # Confidence interval
            ci_low, ci_high = stats.t.interval(
                self.confidence, len(values)-1, loc=mean_val, scale=sem_val
            )
            
            # Normality test
            if len(values) >= 3:
                shapiro_stat, shapiro_p = stats.shapiro(values)
                is_normal = shapiro_p > 0.05
            else:
                shapiro_stat, shapiro_p = None, None
                is_normal = True  # Assume normal for small samples
            
            config_stats[metric_name] = {
                "n_seeds": len(values),
                "values": values.tolist(),
                "mean": mean_val,
                "std": std_val,
                "sem": sem_val,
                "min": np.min(values),
                "max": np.max(values),
                "median": np.median(values),
                "ci_low": ci_low,
                "ci_high": ci_high,
                "ci_width": ci_high - ci_low,
                "cv": std_val / mean_val if mean_val != 0 else 0,  # Coefficient of variation
                "shapiro_stat": shapiro_stat,
                "shapiro_p": shapiro_p,
                "is_normal": is_normal
            }
        
        self.analysis[domain]["experiments"][config_name] = config_stats
        
        print(f"✅ {config_name}: {len(results_list)} seeds analyzed")
    
    def perform_pairwise_comparisons(self, domain, config_groups):
        """Perform statistical comparisons between configurations."""
        configs = list(self.analysis[domain]["experiments"].keys())
        
        if len(configs) < 2:
            print(f"⚠️ {domain.upper()}: Need at least 2 configs for comparisons")
            return
        
        # Determine primary metric
        primary_metric = "eval_loss" if domain == "nlp" else "test_acc"
        
        comparisons = {}
        
        # All pairwise comparisons
        for i, config1 in enumerate(configs):
            for j, config2 in enumerate(configs[i+1:], i+1):
                
                stats1 = self.analysis[domain]["experiments"][config1].get(primary_metric)
                stats2 = self.analysis[domain]["experiments"][config2].get(primary_metric)
                
                if not stats1 or not stats2:
                    continue
                
                values1 = np.array(stats1["values"])
                values2 = np.array(stats2["values"])
                
                # Perform t-test
                if stats1["is_normal"] and stats2["is_normal"]:
                    # Welch's t-test (unequal variances)
                    t_stat, p_value = stats.ttest_ind(values1, values2, equal_var=False)
                    test_type = "welch_t_test"
                else:
                    # Mann-Whitney U test (non-parametric)
                    u_stat, p_value = stats.mannwhitneyu(values1, values2, alternative='two-sided')
                    t_stat = u_stat
                    test_type = "mann_whitney_u"
                
                # Effect size (Cohen's d)
                pooled_std = np.sqrt(((len(values1)-1)*np.var(values1, ddof=1) + 
                                    (len(values2)-1)*np.var(values2, ddof=1)) / 
                                   (len(values1) + len(values2) - 2))
                cohens_d = (np.mean(values1) - np.mean(values2)) / pooled_std
                
                # Practical significance
                mean_diff = np.mean(values1) - np.mean(values2)
                percent_diff = (mean_diff / np.mean(values2)) * 100 if np.mean(values2) != 0 else 0
                
                # Determine winner
                if domain == "nlp":
                    # Lower is better for loss
                    winner = config1 if np.mean(values1) < np.mean(values2) else config2
                    improvement = abs(percent_diff)
                else:
                    # Higher is better for accuracy
                    winner = config1 if np.mean(values1) > np.mean(values2) else config2
                    improvement = abs(percent_diff)
                
                comparison_key = f"{config1}_vs_{config2}"
                comparisons[comparison_key] = {
                    "config1": config1,
                    "config2": config2,
                    "metric": primary_metric,
                    "test_type": test_type,
                    "statistic": t_stat,
                    "p_value": p_value,
                    "is_significant": p_value < self.alpha,
                    "cohens_d": cohens_d,
                    "effect_size_interpretation": self.interpret_effect_size(abs(cohens_d)),
                    "mean_diff": mean_diff,
                    "percent_diff": percent_diff,
                    "improvement_pct": improvement,
                    "winner": winner,
                    "n1": len(values1),
                    "n2": len(values2),
                    "mean1": np.mean(values1),
                    "mean2": np.mean(values2),
                    "std1": np.std(values1, ddof=1),
                    "std2": np.std(values2, ddof=1)
                }
        
        self.analysis[domain]["comparisons"] = comparisons
        
        print(f"✅ {domain.upper()}: {len(comparisons)} pairwise comparisons completed")
    
    def interpret_effect_size(self, d):
        """Interpret Cohen's d effect size."""
        if d < 0.2:
            return "negligible"
        elif d < 0.5:
            return "small"
        elif d < 0.8:
            return "medium"
        else:
            return "large"
    
    def generate_domain_summary(self, domain, config_groups):
        """Generate summary statistics for a domain."""
        experiments = self.analysis[domain]["experiments"]
        comparisons = self.analysis[domain]["comparisons"]
        
        if not experiments:
            return
        
        # Find best performing configuration
        primary_metric = "eval_loss" if domain == "nlp" else "test_acc"
        
        best_config = None
        best_value = float('inf') if domain == "nlp" else float('-inf')
        
        for config_name, stats in experiments.items():
            if primary_metric not in stats:
                continue
                
            mean_val = stats[primary_metric]["mean"]
            
            if domain == "nlp" and mean_val < best_value:
                best_value = mean_val
                best_config = config_name
            elif domain == "vision" and mean_val > best_value:
                best_value = mean_val
                best_config = config_name
        
        # Count significant improvements
        significant_comparisons = [c for c in comparisons.values() if c["is_significant"]]
        total_comparisons = len(comparisons)
        
        # Calculate overall statistics
        all_effect_sizes = [abs(c["cohens_d"]) for c in comparisons.values()]
        mean_effect_size = np.mean(all_effect_sizes) if all_effect_sizes else 0
        
        summary = {
            "domain": domain,
            "total_configurations": len(experiments),
            "total_comparisons": total_comparisons,
            "significant_comparisons": len(significant_comparisons),
            "significance_rate": len(significant_comparisons) / total_comparisons if total_comparisons > 0 else 0,
            "best_configuration": best_config,
            "best_value": best_value,
            "mean_effect_size": mean_effect_size,
            "effect_size_interpretation": self.interpret_effect_size(mean_effect_size),
            "primary_metric": primary_metric
        }
        
        self.analysis[domain]["summary"] = summary
        
        print(f"✅ {domain.upper()} summary: {best_config} is best with {primary_metric}={best_value:.4f}")
    
    def generate_publication_report(self):
        """Generate a publication-ready statistical report."""
        report_lines = []
        
        report_lines.append("# Comprehensive Statistical Analysis Report")
        report_lines.append("## paGLU Multi-Seed Experimental Validation")
        report_lines.append("")
        report_lines.append(f"**Analysis Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"**Seeds Used:** {self.metadata.get('seeds', 'Unknown')}")
        report_lines.append(f"**Significance Level:** α = {self.alpha}")
        report_lines.append(f"**Confidence Level:** {self.confidence*100}%")
        report_lines.append("")
        
        # Executive Summary
        report_lines.append("## Executive Summary")
        report_lines.append("")
        
        for domain in ["nlp", "vision"]:
            summary = self.analysis[domain]["summary"]
            if not summary:
                continue
                
            domain_name = "Language Modeling (GPT-2)" if domain == "nlp" else "Image Classification (CIFAR-10)"
            report_lines.append(f"### {domain_name}")
            report_lines.append("")
            report_lines.append(f"- **Best Configuration:** {summary['best_configuration']}")
            report_lines.append(f"- **Best {summary['primary_metric'].replace('_', ' ').title()}:** {summary['best_value']:.4f}")
            report_lines.append(f"- **Statistical Comparisons:** {summary['significant_comparisons']}/{summary['total_comparisons']} significant")
            report_lines.append(f"- **Mean Effect Size:** {summary['mean_effect_size']:.3f} ({summary['effect_size_interpretation']})")
            report_lines.append("")
        
        # Detailed Results
        for domain in ["nlp", "vision"]:
            if not self.analysis[domain]["experiments"]:
                continue
                
            domain_name = "Language Modeling Results" if domain == "nlp" else "Image Classification Results"
            report_lines.append(f"## {domain_name}")
            report_lines.append("")
            
            # Configuration results table
            report_lines.append("### Configuration Performance")
            report_lines.append("")
            
            experiments = self.analysis[domain]["experiments"]
            primary_metric = "eval_loss" if domain == "nlp" else "test_acc"
            
            # Table header
            report_lines.append("| Configuration | N | Mean | Std | 95% CI | CV |")
            report_lines.append("|---------------|---|------|-----|--------|-----|")
            
            for config_name, stats in experiments.items():
                if primary_metric not in stats:
                    continue
                    
                metric_stats = stats[primary_metric]
                report_lines.append(
                    f"| {config_name} | {metric_stats['n_seeds']} | "
                    f"{metric_stats['mean']:.4f} | {metric_stats['std']:.4f} | "
                    f"[{metric_stats['ci_low']:.4f}, {metric_stats['ci_high']:.4f}] | "
                    f"{metric_stats['cv']:.3f} |"
                )
            
            report_lines.append("")
            
            # Statistical comparisons
            report_lines.append("### Statistical Comparisons")
            report_lines.append("")
            
            comparisons = self.analysis[domain]["comparisons"]
            if comparisons:
                report_lines.append("| Comparison | Test | p-value | Significant | Effect Size | Improvement |")
                report_lines.append("|------------|------|---------|-------------|-------------|-------------|")
                
                for comp_name, comp_stats in comparisons.items():
                    sig_marker = "✅" if comp_stats["is_significant"] else "❌"
                    report_lines.append(
                        f"| {comp_stats['config1']} vs {comp_stats['config2']} | "
                        f"{comp_stats['test_type']} | {comp_stats['p_value']:.4f} | "
                        f"{sig_marker} | {abs(comp_stats['cohens_d']):.3f} ({comp_stats['effect_size_interpretation']}) | "
                        f"{comp_stats['improvement_pct']:.2f}% |"
                    )
                
                report_lines.append("")
            
            # Key findings
            report_lines.append("### Key Findings")
            report_lines.append("")
            
            summary = self.analysis[domain]["summary"]
            significant_comps = [c for c in comparisons.values() if c["is_significant"]]
            
            if significant_comps:
                best_improvement = max(significant_comps, key=lambda x: x["improvement_pct"])
                report_lines.append(f"- **Largest significant improvement:** {best_improvement['improvement_pct']:.2f}% "
                                  f"({best_improvement['winner']} vs competitor)")
                report_lines.append(f"- **Statistical power:** {len(significant_comps)}/{len(comparisons)} comparisons significant")
                report_lines.append(f"- **Effect sizes:** Mean = {summary['mean_effect_size']:.3f} ({summary['effect_size_interpretation']})")
            else:
                report_lines.append("- No statistically significant differences found")
            
            report_lines.append("")
        
        # Methodology
        report_lines.append("## Methodology")
        report_lines.append("")
        report_lines.append("### Statistical Tests")
        report_lines.append("- **Normality:** Shapiro-Wilk test")
        report_lines.append("- **Parametric comparisons:** Welch's t-test (unequal variances)")
        report_lines.append("- **Non-parametric comparisons:** Mann-Whitney U test")
        report_lines.append("- **Effect size:** Cohen's d")
        report_lines.append("- **Multiple comparisons:** No correction applied (exploratory analysis)")
        report_lines.append("")
        
        report_lines.append("### Interpretation Guidelines")
        report_lines.append("- **Effect sizes:** Small (0.2), Medium (0.5), Large (0.8)")
        report_lines.append("- **Statistical significance:** p < 0.05")
        report_lines.append("- **Practical significance:** >1% improvement considered meaningful")
        report_lines.append("")
        
        # Publication readiness assessment
        report_lines.append("## Publication Readiness Assessment")
        report_lines.append("")
        
        total_significant = sum(len([c for c in self.analysis[d]["comparisons"].values() if c["is_significant"]]) 
                              for d in ["nlp", "vision"])
        total_comparisons = sum(len(self.analysis[d]["comparisons"]) for d in ["nlp", "vision"])
        
        readiness_score = 0
        criteria = []
        
        # Multi-seed validation
        min_seeds_met = all(
            all(stats.get("eval_loss" if domain == "nlp" else "test_acc", {}).get("n_seeds", 0) >= self.min_seeds
                for stats in self.analysis[domain]["experiments"].values())
            for domain in ["nlp", "vision"]
            if self.analysis[domain]["experiments"]
        )
        
        if min_seeds_met:
            readiness_score += 3
            criteria.append("✅ Multi-seed validation (≥3 seeds per configuration)")
        else:
            criteria.append("❌ Multi-seed validation (need ≥3 seeds per configuration)")
        
        # Statistical significance
        if total_significant > 0:
            readiness_score += 3
            criteria.append(f"✅ Statistical significance ({total_significant}/{total_comparisons} comparisons)")
        else:
            criteria.append("❌ Statistical significance (no significant differences found)")
        
        # Effect sizes
        mean_effect_sizes = [self.analysis[d]["summary"].get("mean_effect_size", 0) 
                           for d in ["nlp", "vision"] if self.analysis[d]["summary"]]
        if mean_effect_sizes and max(mean_effect_sizes) >= 0.2:
            readiness_score += 2
            criteria.append(f"✅ Meaningful effect sizes (max = {max(mean_effect_sizes):.3f})")
        else:
            criteria.append("❌ Meaningful effect sizes (all < 0.2)")
        
        # Generalizability (multiple domains)
        domains_with_results = sum(1 for d in ["nlp", "vision"] if self.analysis[d]["experiments"])
        if domains_with_results >= 2:
            readiness_score += 2
            criteria.append("✅ Generalizability (multiple domains tested)")
        else:
            criteria.append("❌ Generalizability (need multiple domains)")
        
        report_lines.append(f"**Overall Readiness Score: {readiness_score}/10**")
        report_lines.append("")
        
        for criterion in criteria:
            report_lines.append(f"- {criterion}")
        
        report_lines.append("")
        
        if readiness_score >= 8:
            report_lines.append("🟢 **READY FOR PUBLICATION** - Strong statistical evidence")
        elif readiness_score >= 6:
            report_lines.append("🟡 **CONDITIONALLY READY** - Address remaining issues")
        else:
            report_lines.append("🔴 **NOT READY** - Significant methodological improvements needed")
        
        # Save report
        report_file = self.output_dir / "comprehensive_statistical_report.md"
        with open(report_file, 'w') as f:
            f.write('\n'.join(report_lines))
        
        print(f"📊 Comprehensive report saved to: {report_file}")
        return readiness_score
    
    def run_complete_analysis(self):
        """Run the complete statistical analysis pipeline."""
        print("🔬 Starting Comprehensive Statistical Analysis")
        print("=" * 60)
        
        # Analyze each domain
        for domain in ["nlp", "vision"]:
            self.analyze_domain_results(domain)
        
        # Generate comprehensive report
        readiness_score = self.generate_publication_report()
        
        # Save analysis results
        analysis_file = self.output_dir / "statistical_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(self.analysis, f, indent=2, default=str)
        
        print("=" * 60)
        print(f"✅ Analysis complete! Publication readiness: {readiness_score}/10")
        print(f"📁 Results saved to: {self.output_dir}")
        
        return self.analysis, readiness_score


def main():
    """Main execution function."""
    args = parse_args()
    
    if not Path(args.results_file).exists():
        print(f"❌ Results file not found: {args.results_file}")
        return
    
    # Create analyzer
    analyzer = ComprehensiveStatisticalAnalyzer(
        args.results_file, 
        args.output_dir,
        args.alpha,
        args.confidence,
        args.min_seeds
    )
    
    # Run analysis
    analysis, readiness_score = analyzer.run_complete_analysis()
    
    return analysis, readiness_score


if __name__ == "__main__":
    main() 