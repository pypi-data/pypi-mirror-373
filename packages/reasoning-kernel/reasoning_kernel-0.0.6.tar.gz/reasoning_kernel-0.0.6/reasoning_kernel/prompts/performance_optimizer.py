"""
Performance Optimizer for MSA Prompt Templates

This module provides performance optimization capabilities for the MSA prompt template system,
including caching strategies, response processing optimization, and production performance tuning.
"""

import asyncio
import hashlib
import json
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for prompt template execution"""

    template_name: str
    execution_time: float
    tokens_used: int
    cache_hit: bool
    response_size: int
    timestamp: datetime
    success: bool
    error: Optional[str] = None


@dataclass
class CacheEntry:
    """Cache entry for prompt responses"""

    key: str
    response: Any
    timestamp: datetime
    access_count: int
    template_name: str
    ttl_seconds: int = 3600  # 1 hour default TTL


@dataclass
class OptimizationConfig:
    """Configuration for performance optimization"""

    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    max_cache_size: int = 1000
    enable_response_compression: bool = True
    enable_batch_processing: bool = True
    max_batch_size: int = 5
    enable_metrics_collection: bool = True
    metrics_retention_days: int = 7
    cache_cleanup_interval_seconds: int = 300  # 5 minutes


class PromptTemplateOptimizer:
    """Performance optimizer for MSA prompt templates"""

    def __init__(self, config: OptimizationConfig = None):
        self.config = config or OptimizationConfig()
        self._cache: Dict[str, CacheEntry] = {}
        self._metrics: List[PerformanceMetrics] = []
        self._last_cleanup = datetime.now()
        self._optimization_stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "total_requests": 0,
            "total_execution_time": 0.0,
            "total_tokens_saved": 0,
        }

    def generate_cache_key(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Generate a cache key for template execution"""
        # Create a deterministic hash of template name and variables
        content = json.dumps({"template": template_name, "variables": variables}, sort_keys=True)

        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def get_cached_response(self, cache_key: str) -> Optional[Any]:
        """Get cached response if available and valid"""
        if not self.config.enable_caching:
            return None

        entry = self._cache.get(cache_key)
        if not entry:
            return None

        # Check TTL
        if datetime.now() - entry.timestamp > timedelta(seconds=entry.ttl_seconds):
            # Entry expired, remove it
            del self._cache[cache_key]
            return None

        # Update access count
        entry.access_count += 1
        self._optimization_stats["cache_hits"] += 1

        logger.debug(f"Cache hit for key {cache_key}")
        return entry.response

    async def cache_response(
        self, cache_key: str, response: Any, template_name: str, ttl_seconds: Optional[int] = None
    ):
        """Cache a response"""
        if not self.config.enable_caching:
            return

        # Check cache size limit
        if len(self._cache) >= self.config.max_cache_size:
            await self._cleanup_cache(force=True)

        ttl = ttl_seconds or self.config.cache_ttl_seconds

        entry = CacheEntry(
            key=cache_key,
            response=response,
            timestamp=datetime.now(),
            access_count=1,
            template_name=template_name,
            ttl_seconds=ttl,
        )

        self._cache[cache_key] = entry
        logger.debug(f"Cached response for key {cache_key}")

    async def optimize_template_execution(
        self, template_name: str, variables: Dict[str, Any], execution_func, **kwargs
    ) -> Tuple[Any, PerformanceMetrics]:
        """Optimize template execution with caching and metrics"""
        start_time = time.time()
        cache_key = self.generate_cache_key(template_name, variables)

        # Try cache first
        cached_response = await self.get_cached_response(cache_key)
        if cached_response:
            execution_time = time.time() - start_time

            metrics = PerformanceMetrics(
                template_name=template_name,
                execution_time=execution_time,
                tokens_used=0,  # No tokens used for cached response
                cache_hit=True,
                response_size=len(str(cached_response)),
                timestamp=datetime.now(),
                success=True,
            )

            await self._record_metrics(metrics)
            return cached_response, metrics

        # Cache miss - execute template
        self._optimization_stats["cache_misses"] += 1

        try:
            # Execute the template
            response = await execution_func(**kwargs)
            execution_time = time.time() - start_time

            # Extract metrics from response
            tokens_used = 0
            if hasattr(response, "usage"):
                tokens_used = response.usage.get("total_tokens", 0)

            # Cache the response
            await self.cache_response(cache_key, response, template_name)

            metrics = PerformanceMetrics(
                template_name=template_name,
                execution_time=execution_time,
                tokens_used=tokens_used,
                cache_hit=False,
                response_size=len(str(response)),
                timestamp=datetime.now(),
                success=True,
            )

            await self._record_metrics(metrics)
            return response, metrics

        except Exception as e:
            execution_time = time.time() - start_time

            metrics = PerformanceMetrics(
                template_name=template_name,
                execution_time=execution_time,
                tokens_used=0,
                cache_hit=False,
                response_size=0,
                timestamp=datetime.now(),
                success=False,
                error=str(e),
            )

            await self._record_metrics(metrics)
            raise

    async def optimize_batch_execution(
        self, batch_requests: List[Tuple[str, Dict[str, Any]]], execution_func, **kwargs
    ) -> List[Tuple[Any, PerformanceMetrics]]:
        """Optimize batch execution of templates"""
        if not self.config.enable_batch_processing or len(batch_requests) <= 1:
            # Execute individually
            results = []
            for template_name, variables in batch_requests:
                result = await self.optimize_template_execution(template_name, variables, execution_func, **kwargs)
                results.append(result)
            return results

        # Batch processing
        results = []
        batch_size = min(len(batch_requests), self.config.max_batch_size)

        for i in range(0, len(batch_requests), batch_size):
            batch = batch_requests[i : i + batch_size]

            # Process batch concurrently
            batch_tasks = []
            for template_name, variables in batch:
                task = self.optimize_template_execution(template_name, variables, execution_func, **kwargs)
                batch_tasks.append(task)

            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    # Handle exception
                    error_metrics = PerformanceMetrics(
                        template_name="batch_error",
                        execution_time=0.0,
                        tokens_used=0,
                        cache_hit=False,
                        response_size=0,
                        timestamp=datetime.now(),
                        success=False,
                        error=str(result),
                    )
                    results.append((None, error_metrics))
                else:
                    results.append(result)

        return results

    async def _record_metrics(self, metrics: PerformanceMetrics):
        """Record performance metrics"""
        if not self.config.enable_metrics_collection:
            return

        self._metrics.append(metrics)

        # Update optimization stats
        self._optimization_stats["total_requests"] += 1
        self._optimization_stats["total_execution_time"] += metrics.execution_time

        if metrics.cache_hit:
            # Estimate tokens saved (average tokens per template)
            avg_tokens = self._calculate_average_tokens(metrics.template_name)
            self._optimization_stats["total_tokens_saved"] += avg_tokens

        # Cleanup old metrics
        await self._cleanup_metrics()

    def _calculate_average_tokens(self, template_name: str) -> int:
        """Calculate average tokens for a template"""
        template_metrics = [
            m for m in self._metrics if m.template_name == template_name and not m.cache_hit and m.success
        ]

        if not template_metrics:
            return 100  # Default estimate

        total_tokens = sum(m.tokens_used for m in template_metrics)
        return total_tokens // len(template_metrics)

    async def _cleanup_cache(self, force: bool = False):
        """Cleanup expired cache entries"""
        if not force and datetime.now() - self._last_cleanup < timedelta(
            seconds=self.config.cache_cleanup_interval_seconds
        ):
            return

        current_time = datetime.now()
        expired_keys = []

        for key, entry in self._cache.items():
            if current_time - entry.timestamp > timedelta(seconds=entry.ttl_seconds):
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

        # If still over limit, remove least recently used entries
        if force and len(self._cache) >= self.config.max_cache_size:
            # Sort by access count and timestamp
            sorted_entries = sorted(self._cache.items(), key=lambda x: (x[1].access_count, x[1].timestamp))

            # Remove oldest, least accessed entries
            entries_to_remove = len(self._cache) - self.config.max_cache_size + 100  # Remove extra for buffer
            for i in range(min(entries_to_remove, len(sorted_entries))):
                key = sorted_entries[i][0]
                del self._cache[key]

        self._last_cleanup = current_time
        logger.debug(f"Cache cleanup completed. Removed {len(expired_keys)} expired entries")

    async def _cleanup_metrics(self):
        """Cleanup old metrics"""
        cutoff_date = datetime.now() - timedelta(days=self.config.metrics_retention_days)
        self._metrics = [m for m in self._metrics if m.timestamp > cutoff_date]

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        if not self._metrics:
            return {"error": "No metrics available"}

        # Calculate statistics
        total_requests = len(self._metrics)
        successful_requests = len([m for m in self._metrics if m.success])
        cache_hits = len([m for m in self._metrics if m.cache_hit])

        avg_execution_time = sum(m.execution_time for m in self._metrics) / total_requests
        total_tokens = sum(m.tokens_used for m in self._metrics)

        # Template-specific stats
        template_stats = {}
        for metrics in self._metrics:
            template = metrics.template_name
            if template not in template_stats:
                template_stats[template] = {
                    "requests": 0,
                    "cache_hits": 0,
                    "avg_execution_time": 0.0,
                    "total_tokens": 0,
                    "success_rate": 0.0,
                }

            stats = template_stats[template]
            stats["requests"] += 1
            if metrics.cache_hit:
                stats["cache_hits"] += 1
            stats["avg_execution_time"] += metrics.execution_time
            stats["total_tokens"] += metrics.tokens_used
            if metrics.success:
                stats["success_rate"] += 1

        # Finalize template stats
        for template, stats in template_stats.items():
            stats["cache_hit_rate"] = stats["cache_hits"] / stats["requests"]
            stats["avg_execution_time"] = stats["avg_execution_time"] / stats["requests"]
            stats["success_rate"] = stats["success_rate"] / stats["requests"]

        return {
            "summary": {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "success_rate": successful_requests / total_requests,
                "cache_hit_rate": cache_hits / total_requests,
                "avg_execution_time": avg_execution_time,
                "total_tokens_used": total_tokens,
                "tokens_saved_by_caching": self._optimization_stats["total_tokens_saved"],
                "cache_size": len(self._cache),
            },
            "template_stats": template_stats,
            "optimization_stats": self._optimization_stats,
            "config": asdict(self.config),
        }

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache-specific statistics"""
        if not self._cache:
            return {"cache_size": 0, "entries": []}

        entries = []
        for key, entry in self._cache.items():
            entries.append(
                {
                    "key": key,
                    "template": entry.template_name,
                    "age_seconds": (datetime.now() - entry.timestamp).total_seconds(),
                    "access_count": entry.access_count,
                    "ttl_seconds": entry.ttl_seconds,
                }
            )

        # Sort by access count descending
        entries.sort(key=lambda x: x["access_count"], reverse=True)

        return {
            "cache_size": len(self._cache),
            "max_cache_size": self.config.max_cache_size,
            "hit_rate": self._optimization_stats["cache_hits"] / max(1, self._optimization_stats["total_requests"]),
            "entries": entries[:20],  # Top 20 entries
        }

    async def clear_cache(self, template_name: Optional[str] = None):
        """Clear cache entries"""
        if template_name:
            # Clear cache for specific template
            keys_to_remove = [key for key, entry in self._cache.items() if entry.template_name == template_name]
            for key in keys_to_remove:
                del self._cache[key]
            logger.info(f"Cleared cache for template: {template_name}")
        else:
            # Clear all cache
            self._cache.clear()
            logger.info("Cleared all cache entries")

    async def optimize_template_parameters(self, template_name: str) -> Dict[str, Any]:
        """Analyze and suggest optimizations for a specific template"""
        template_metrics = [m for m in self._metrics if m.template_name == template_name]

        if not template_metrics:
            return {"error": f"No metrics found for template: {template_name}"}

        # Analyze performance patterns
        avg_execution_time = sum(m.execution_time for m in template_metrics) / len(template_metrics)
        avg_tokens = sum(m.tokens_used for m in template_metrics if not m.cache_hit) / max(
            1, len([m for m in template_metrics if not m.cache_hit])
        )
        cache_hit_rate = len([m for m in template_metrics if m.cache_hit]) / len(template_metrics)

        # Advanced performance analysis
        performance_analysis = await self._analyze_performance_patterns(template_metrics)
        optimization_suggestions = await self._generate_optimization_suggestions(
            template_name, template_metrics, performance_analysis
        )

        recommendations = []

        # Performance recommendations
        if avg_execution_time > 5.0:
            recommendations.append("Consider reducing template complexity or max_tokens")

        if avg_tokens > 2000:
            recommendations.append("Template generates high token usage - consider optimization")

        if cache_hit_rate < 0.3:
            recommendations.append("Low cache hit rate - consider increasing cache TTL")

        if cache_hit_rate > 0.8:
            recommendations.append("High cache hit rate - template is well-optimized for caching")

        # Add advanced recommendations
        recommendations.extend(optimization_suggestions)

        return {
            "template_name": template_name,
            "metrics": {
                "avg_execution_time": avg_execution_time,
                "avg_tokens": avg_tokens,
                "cache_hit_rate": cache_hit_rate,
                "total_requests": len(template_metrics),
            },
            "performance_analysis": performance_analysis,
            "recommendations": recommendations,
            "optimization_score": await self._calculate_optimization_score(template_metrics),
        }

    async def _analyze_performance_patterns(self, metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Analyze detailed performance patterns"""
        if not metrics:
            return {}

        # Time-based analysis
        execution_times = [m.execution_time for m in metrics]
        token_usage = [m.tokens_used for m in metrics if not m.cache_hit]

        # Statistical analysis
        import statistics

        analysis = {
            "execution_time": {
                "mean": statistics.mean(execution_times),
                "median": statistics.median(execution_times),
                "std_dev": statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
                "min": min(execution_times),
                "max": max(execution_times),
                "p95": (
                    statistics.quantiles(execution_times, n=20)[18]
                    if len(execution_times) >= 20
                    else max(execution_times)
                ),
            },
            "token_usage": {
                "mean": statistics.mean(token_usage) if token_usage else 0,
                "median": statistics.median(token_usage) if token_usage else 0,
                "std_dev": statistics.stdev(token_usage) if len(token_usage) > 1 else 0,
                "min": min(token_usage) if token_usage else 0,
                "max": max(token_usage) if token_usage else 0,
            },
            "cache_performance": {
                "hit_rate": len([m for m in metrics if m.cache_hit]) / len(metrics),
                "miss_rate": len([m for m in metrics if not m.cache_hit]) / len(metrics),
                "avg_response_size": sum(m.response_size for m in metrics) / len(metrics),
            },
            "error_analysis": {
                "error_rate": len([m for m in metrics if not m.success]) / len(metrics),
                "total_errors": len([m for m in metrics if not m.success]),
            },
        }

        return analysis

    async def _generate_optimization_suggestions(
        self, template_name: str, metrics: List[PerformanceMetrics], analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate specific optimization suggestions"""
        suggestions = []

        # Execution time optimization
        if analysis.get("execution_time", {}).get("std_dev", 0) > 2.0:
            suggestions.append("High variance in execution time - investigate inconsistent performance")

        if analysis.get("execution_time", {}).get("p95", 0) > analysis.get("execution_time", {}).get("mean", 0) * 2:
            suggestions.append("Long tail latency detected - consider timeout optimization")

        # Token usage optimization
        token_std = analysis.get("token_usage", {}).get("std_dev", 0)
        token_mean = analysis.get("token_usage", {}).get("mean", 0)
        if token_mean > 0 and token_std / token_mean > 0.5:
            suggestions.append("High variance in token usage - consider prompt standardization")

        # Cache optimization
        cache_hit_rate = analysis.get("cache_performance", {}).get("hit_rate", 0)
        if cache_hit_rate < 0.2:
            suggestions.append("Very low cache hit rate - review cache key generation strategy")
        elif cache_hit_rate > 0.9:
            suggestions.append("Excellent cache performance - consider extending cache TTL")

        # Error rate optimization
        error_rate = analysis.get("error_analysis", {}).get("error_rate", 0)
        if error_rate > 0.05:
            suggestions.append("High error rate detected - review error handling and input validation")

        # Response size optimization
        avg_response_size = analysis.get("cache_performance", {}).get("avg_response_size", 0)
        if avg_response_size > 10000:  # 10KB
            suggestions.append("Large response sizes - consider response compression or truncation")

        return suggestions

    async def _calculate_optimization_score(self, metrics: List[PerformanceMetrics]) -> float:
        """Calculate overall optimization score (0.0 - 1.0)"""
        if not metrics:
            return 0.0

        score = 0.0

        # Performance score (40% weight)
        avg_execution_time = sum(m.execution_time for m in metrics) / len(metrics)
        if avg_execution_time < 2.0:
            score += 0.4
        elif avg_execution_time < 5.0:
            score += 0.3
        elif avg_execution_time < 10.0:
            score += 0.2
        else:
            score += 0.1

        # Cache efficiency score (30% weight)
        cache_hit_rate = len([m for m in metrics if m.cache_hit]) / len(metrics)
        score += cache_hit_rate * 0.3

        # Reliability score (20% weight)
        success_rate = len([m for m in metrics if m.success]) / len(metrics)
        score += success_rate * 0.2

        # Token efficiency score (10% weight)
        non_cached_metrics = [m for m in metrics if not m.cache_hit]
        if non_cached_metrics:
            avg_tokens = sum(m.tokens_used for m in non_cached_metrics) / len(non_cached_metrics)
            if avg_tokens < 1000:
                score += 0.1
            elif avg_tokens < 2000:
                score += 0.07
            elif avg_tokens < 3000:
                score += 0.05
            else:
                score += 0.02

        return min(1.0, score)

    async def optimize_cache_strategy(self, template_name: str) -> Dict[str, Any]:
        """Optimize caching strategy for a specific template"""
        template_metrics = [m for m in self._metrics if m.template_name == template_name]

        if not template_metrics:
            return {"error": f"No metrics found for template: {template_name}"}

        # Analyze cache patterns
        cache_analysis = await self._analyze_cache_patterns(template_metrics)

        # Generate cache optimization recommendations
        cache_recommendations = await self._generate_cache_recommendations(cache_analysis)

        # Calculate optimal cache parameters
        optimal_params = await self._calculate_optimal_cache_params(template_metrics)

        return {
            "template_name": template_name,
            "cache_analysis": cache_analysis,
            "recommendations": cache_recommendations,
            "optimal_parameters": optimal_params,
            "current_performance": {
                "hit_rate": cache_analysis["hit_rate"],
                "avg_response_time": cache_analysis["avg_response_time"],
                "cache_efficiency": cache_analysis["cache_efficiency"],
            },
        }

    async def _analyze_cache_patterns(self, metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Analyze caching patterns and effectiveness"""
        cache_hits = [m for m in metrics if m.cache_hit]
        cache_misses = [m for m in metrics if not m.cache_hit]

        total_requests = len(metrics)
        hit_rate = len(cache_hits) / total_requests if total_requests > 0 else 0

        # Time-based analysis
        hit_response_times = [m.execution_time for m in cache_hits]
        miss_response_times = [m.execution_time for m in cache_misses]

        avg_hit_time = sum(hit_response_times) / len(hit_response_times) if hit_response_times else 0
        avg_miss_time = sum(miss_response_times) / len(miss_response_times) if miss_response_times else 0

        # Cache efficiency calculation
        time_saved = sum(avg_miss_time - hit_time for hit_time in hit_response_times)
        cache_efficiency = time_saved / (total_requests * avg_miss_time) if avg_miss_time > 0 else 0

        return {
            "hit_rate": hit_rate,
            "miss_rate": 1 - hit_rate,
            "total_requests": total_requests,
            "cache_hits": len(cache_hits),
            "cache_misses": len(cache_misses),
            "avg_hit_time": avg_hit_time,
            "avg_miss_time": avg_miss_time,
            "avg_response_time": sum(m.execution_time for m in metrics) / total_requests,
            "time_saved": time_saved,
            "cache_efficiency": cache_efficiency,
        }

    async def _generate_cache_recommendations(self, cache_analysis: Dict[str, Any]) -> List[str]:
        """Generate cache optimization recommendations"""
        recommendations = []

        hit_rate = cache_analysis["hit_rate"]
        cache_efficiency = cache_analysis["cache_efficiency"]
        avg_hit_time = cache_analysis["avg_hit_time"]
        avg_miss_time = cache_analysis["avg_miss_time"]

        # Hit rate recommendations
        if hit_rate < 0.2:
            recommendations.append("Very low cache hit rate - consider reviewing cache key generation")
            recommendations.append("Increase cache TTL to improve hit rates")
        elif hit_rate < 0.5:
            recommendations.append("Moderate cache hit rate - optimize cache key strategy")
        elif hit_rate > 0.8:
            recommendations.append("Excellent cache hit rate - consider increasing cache size")

        # Efficiency recommendations
        if cache_efficiency < 0.3:
            recommendations.append("Low cache efficiency - review caching strategy")
        elif cache_efficiency > 0.7:
            recommendations.append("High cache efficiency - current strategy is effective")

        # Response time recommendations
        if avg_hit_time > 0.5:
            recommendations.append("Cache retrieval is slow - consider cache optimization")

        if avg_miss_time > 10.0:
            recommendations.append("Cache misses are expensive - prioritize cache hits")

        return recommendations

    async def _calculate_optimal_cache_params(self, metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Calculate optimal cache parameters"""
        # Analyze request patterns
        request_intervals = []
        timestamps = [m.timestamp for m in metrics]
        timestamps.sort()

        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i - 1]).total_seconds()
            request_intervals.append(interval)

        # Calculate optimal TTL based on request patterns
        if request_intervals:
            import statistics

            median_interval = statistics.median(request_intervals)
            optimal_ttl = max(300, min(3600, median_interval * 5))  # 5x median interval, capped
        else:
            optimal_ttl = 1800  # Default 30 minutes

        # Calculate optimal cache size
        unique_requests = len(set(self.generate_cache_key(m.template_name, {}) for m in metrics))
        optimal_cache_size = max(100, min(5000, unique_requests * 2))  # 2x unique requests

        return {
            "optimal_ttl_seconds": int(optimal_ttl),
            "optimal_cache_size": optimal_cache_size,
            "recommended_cleanup_interval": max(60, optimal_ttl // 10),
            "cache_warming_recommended": len(metrics) > 100,
        }

    async def auto_tune_performance(self, template_name: Optional[str] = None) -> Dict[str, Any]:
        """Automatically tune performance parameters"""
        if template_name:
            templates_to_tune = [template_name]
        else:
            # Get all templates with metrics
            templates_to_tune = list(set(m.template_name for m in self._metrics))

        tuning_results = {}

        for template in templates_to_tune:
            template_metrics = [m for m in self._metrics if m.template_name == template]

            if len(template_metrics) < 10:  # Need sufficient data
                continue

            # Analyze current performance
            current_analysis = await self._analyze_performance_patterns(template_metrics)

            # Generate tuning recommendations
            tuning_recommendations = await self._generate_tuning_recommendations(template, current_analysis)

            # Calculate performance improvement potential
            improvement_potential = await self._calculate_improvement_potential(template_metrics)

            tuning_results[template] = {
                "current_performance": current_analysis,
                "tuning_recommendations": tuning_recommendations,
                "improvement_potential": improvement_potential,
                "priority": (
                    "high" if improvement_potential > 0.3 else "medium" if improvement_potential > 0.1 else "low"
                ),
            }

        return {
            "tuning_results": tuning_results,
            "summary": {
                "templates_analyzed": len(tuning_results),
                "high_priority_templates": len([t for t in tuning_results.values() if t["priority"] == "high"]),
                "total_improvement_potential": sum(t["improvement_potential"] for t in tuning_results.values()),
            },
        }

    async def _generate_tuning_recommendations(
        self, template_name: str, analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate specific tuning recommendations"""
        recommendations = []

        # Execution time tuning
        exec_time = analysis.get("execution_time", {})
        if exec_time.get("mean", 0) > 5.0:
            recommendations.append(
                {
                    "type": "execution_time",
                    "action": "reduce_max_tokens",
                    "current_value": "unknown",
                    "recommended_value": "reduce by 20%",
                    "expected_improvement": "15-25% faster execution",
                }
            )

        # Cache tuning
        cache_perf = analysis.get("cache_performance", {})
        if cache_perf.get("hit_rate", 0) < 0.4:
            recommendations.append(
                {
                    "type": "cache_optimization",
                    "action": "increase_ttl",
                    "current_value": f"{self.config.cache_ttl_seconds}s",
                    "recommended_value": f"{self.config.cache_ttl_seconds * 2}s",
                    "expected_improvement": "30-50% better cache hit rate",
                }
            )

        # Token usage tuning
        token_usage = analysis.get("token_usage", {})
        if token_usage.get("mean", 0) > 2000:
            recommendations.append(
                {
                    "type": "token_optimization",
                    "action": "optimize_prompt_template",
                    "current_value": f"{token_usage.get('mean', 0):.0f} tokens",
                    "recommended_value": "reduce by 25%",
                    "expected_improvement": "20-30% cost reduction",
                }
            )

        return recommendations

    async def _calculate_improvement_potential(self, metrics: List[PerformanceMetrics]) -> float:
        """Calculate potential performance improvement (0.0 - 1.0)"""
        if not metrics:
            return 0.0

        # Calculate current efficiency
        avg_execution_time = sum(m.execution_time for m in metrics) / len(metrics)
        cache_hit_rate = len([m for m in metrics if m.cache_hit]) / len(metrics)
        success_rate = len([m for m in metrics if m.success]) / len(metrics)

        # Calculate improvement potential
        time_improvement = max(0, (avg_execution_time - 2.0) / avg_execution_time) if avg_execution_time > 2.0 else 0
        cache_improvement = max(0, (0.8 - cache_hit_rate)) if cache_hit_rate < 0.8 else 0
        reliability_improvement = max(0, (1.0 - success_rate)) if success_rate < 1.0 else 0

        # Weighted average
        improvement_potential = time_improvement * 0.4 + cache_improvement * 0.4 + reliability_improvement * 0.2

        return min(1.0, improvement_potential)


# Global optimizer instance
_optimizer: Optional[PromptTemplateOptimizer] = None


def get_optimizer(config: OptimizationConfig = None) -> PromptTemplateOptimizer:
    """Get the global prompt template optimizer"""
    global _optimizer
    if _optimizer is None:
        _optimizer = PromptTemplateOptimizer(config)
    return _optimizer


async def optimize_prompt_execution(
    template_name: str, variables: Dict[str, Any], execution_func, **kwargs
) -> Tuple[Any, PerformanceMetrics]:
    """Convenience function for optimized prompt execution"""
    optimizer = get_optimizer()
    return await optimizer.optimize_template_execution(template_name, variables, execution_func, **kwargs)
