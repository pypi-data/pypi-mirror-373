"""
Real-Time Evolutionary Data Updater

Patent-pending system for streaming evolutionary data integration
with adaptive filtering and anomaly detection.
"""

from typing import Dict, List, Optional, Any, Tuple, Union, Callable, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum, auto
import numpy as np
import logging
from abc import ABC, abstractmethod
import asyncio
import time
import json
from collections import deque, defaultdict
import threading
import queue

try:
    import websocket
    HAS_WEBSOCKET = True
except ImportError:
    HAS_WEBSOCKET = False
    
    class websocket:
        @staticmethod
        def create_connection(url):
            return None

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    
    class redis:
        @staticmethod
        def Redis(*args, **kwargs):
            return None

logger = logging.getLogger(__name__)


class StreamingDataType(Enum):
    """Types of streaming evolutionary data."""
    
    REAL_TIME_SEQUENCING = auto()     # Live sequencing data
    POPULATION_MONITORING = auto()    # Population size/fitness tracking
    ENVIRONMENTAL_SENSORS = auto()    # Environmental conditions
    PHENOTYPE_TRACKING = auto()       # Phenotypic measurements
    EXPRESSION_PROFILING = auto()     # Gene expression monitoring
    FITNESS_ASSAYS = auto()          # Fitness measurements
    DRUG_RESPONSES = auto()          # Drug resistance/response
    METABOLIC_FLUX = auto()          # Metabolic measurements


class UpdateStrategy(Enum):
    """Strategies for real-time data updates."""
    
    IMMEDIATE = auto()               # Process immediately
    BATCHED = auto()                # Batch processing
    WINDOWED = auto()               # Time window processing
    THRESHOLD_BASED = auto()         # Update when threshold reached
    ADAPTIVE = auto()               # Adaptive based on data characteristics


@dataclass
class StreamingDataPoint:
    """
    Single streaming data point.
    
    Patent Feature: Standardized streaming data representation
    with temporal metadata and quality indicators.
    """
    
    data_id: str
    data_type: StreamingDataType
    timestamp: float
    
    # Core data
    values: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Quality indicators
    quality_score: float = 1.0
    confidence: float = 1.0
    is_anomaly: bool = False
    
    # Stream information
    stream_id: str = "default"
    sequence_number: int = 0
    
    # Processing flags
    processed: bool = False
    processing_timestamp: Optional[float] = None
    
    def __post_init__(self):
        """Validate and enrich data point."""
        
        # Ensure timestamp is set
        if self.timestamp <= 0:
            self.timestamp = time.time()
        
        # Add creation metadata
        self.metadata.setdefault('created_at', self.timestamp)
        self.metadata.setdefault('source', 'streaming')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        
        return {
            'data_id': self.data_id,
            'data_type': self.data_type.name,
            'timestamp': self.timestamp,
            'values': self.values,
            'metadata': self.metadata,
            'quality_score': self.quality_score,
            'confidence': self.confidence,
            'is_anomaly': self.is_anomaly,
            'stream_id': self.stream_id,
            'sequence_number': self.sequence_number
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StreamingDataPoint':
        """Create from dictionary."""
        
        data_type = StreamingDataType[data.get('data_type', 'REAL_TIME_SEQUENCING')]
        
        return cls(
            data_id=data.get('data_id', ''),
            data_type=data_type,
            timestamp=data.get('timestamp', time.time()),
            values=data.get('values', {}),
            metadata=data.get('metadata', {}),
            quality_score=data.get('quality_score', 1.0),
            confidence=data.get('confidence', 1.0),
            is_anomaly=data.get('is_anomaly', False),
            stream_id=data.get('stream_id', 'default'),
            sequence_number=data.get('sequence_number', 0)
        )


class AnomalyDetector:
    """
    Real-time anomaly detection for streaming data.
    
    Patent Feature: Multi-method anomaly detection with
    biological knowledge integration and adaptive thresholds.
    """
    
    def __init__(
        self,
        window_size: int = 100,
        contamination_rate: float = 0.1
    ):
        """
        Initialize anomaly detector.
        
        Args:
            window_size: Size of sliding window for detection
            contamination_rate: Expected rate of anomalies
        """
        self.window_size = window_size
        self.contamination_rate = contamination_rate
        
        # Data buffers
        self.data_buffer: deque = deque(maxlen=window_size)
        self.anomaly_history: List[Dict[str, Any]] = []
        
        # Statistical models
        self.baseline_stats = {}
        self.anomaly_thresholds = {}
        
        # Biological constraints
        self.biological_bounds = {
            'fitness': (0.0, 1.0),
            'population_size': (1, 1e6),
            'expression_level': (0.0, 1000.0),
            'mutation_rate': (1e-10, 1e-2),
            'growth_rate': (-10.0, 10.0),
            'drug_concentration': (0.0, 1000.0)
        }
        
        logger.info("Anomaly detector initialized")
    
    def update_baseline(self, data_points: List[StreamingDataPoint]):
        """Update baseline statistics from normal data."""
        
        if not data_points:
            return
        
        # Extract numeric values by key
        value_collections = defaultdict(list)
        
        for point in data_points:
            for key, value in point.values.items():
                if isinstance(value, (int, float)) and not np.isnan(value):
                    value_collections[key].append(value)
        
        # Update baseline statistics
        for key, values in value_collections.items():
            if len(values) >= 10:  # Minimum samples for reliable statistics
                self.baseline_stats[key] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'median': np.median(values),
                    'q25': np.percentile(values, 25),
                    'q75': np.percentile(values, 75),
                    'min': np.min(values),
                    'max': np.max(values),
                    'count': len(values),
                    'last_updated': time.time()
                }
                
                # Set adaptive threshold
                iqr = self.baseline_stats[key]['q75'] - self.baseline_stats[key]['q25']
                threshold = 1.5 * iqr  # Standard outlier threshold
                self.anomaly_thresholds[key] = threshold
        
        logger.info(f"Updated baseline statistics for {len(self.baseline_stats)} features")
    
    def detect_anomalies(self, data_point: StreamingDataPoint) -> Dict[str, Any]:
        """
        Detect anomalies in a streaming data point.
        
        Args:
            data_point: Data point to check for anomalies
            
        Returns:
            Anomaly detection results
        """
        
        anomaly_results = {
            'is_anomaly': False,
            'anomaly_score': 0.0,
            'anomaly_types': [],
            'anomaly_details': {},
            'timestamp': time.time()
        }
        
        # Statistical anomaly detection
        statistical_anomalies = self._detect_statistical_anomalies(data_point)
        
        # Biological constraint violations
        biological_anomalies = self._detect_biological_anomalies(data_point)
        
        # Temporal anomalies
        temporal_anomalies = self._detect_temporal_anomalies(data_point)
        
        # Combine results
        all_anomalies = {
            'statistical': statistical_anomalies,
            'biological': biological_anomalies,
            'temporal': temporal_anomalies
        }
        
        # Calculate overall anomaly score
        max_scores = []
        for anomaly_type, results in all_anomalies.items():
            if results['detected']:
                anomaly_results['anomaly_types'].append(anomaly_type)
                max_scores.append(results['max_score'])
                anomaly_results['anomaly_details'][anomaly_type] = results
        
        if max_scores:
            anomaly_results['is_anomaly'] = True
            anomaly_results['anomaly_score'] = max(max_scores)
            data_point.is_anomaly = True
        
        # Record anomaly
        if anomaly_results['is_anomaly']:
            self._record_anomaly(data_point, anomaly_results)
        
        # Update data buffer
        self.data_buffer.append(data_point)
        
        return anomaly_results
    
    def _detect_statistical_anomalies(self, data_point: StreamingDataPoint) -> Dict[str, Any]:
        """Detect statistical outliers."""
        
        results = {
            'detected': False,
            'max_score': 0.0,
            'outliers': {}
        }
        
        for key, value in data_point.values.items():
            if isinstance(value, (int, float)) and not np.isnan(value):
                if key in self.baseline_stats:
                    stats = self.baseline_stats[key]
                    
                    # Z-score based detection
                    z_score = abs(value - stats['mean']) / (stats['std'] + 1e-12)
                    
                    # IQR based detection
                    iqr_threshold = self.anomaly_thresholds.get(key, 1.5 * stats['std'])
                    is_iqr_outlier = (
                        value < (stats['q25'] - iqr_threshold) or
                        value > (stats['q75'] + iqr_threshold)
                    )
                    
                    # Combine detection methods
                    anomaly_score = z_score / 3.0  # Normalize z-score
                    if is_iqr_outlier:
                        anomaly_score = max(anomaly_score, 0.8)
                    
                    if anomaly_score > 0.5:  # Threshold for anomaly
                        results['detected'] = True
                        results['max_score'] = max(results['max_score'], anomaly_score)
                        results['outliers'][key] = {
                            'value': value,
                            'z_score': z_score,
                            'anomaly_score': anomaly_score,
                            'is_iqr_outlier': is_iqr_outlier
                        }
        
        return results
    
    def _detect_biological_anomalies(self, data_point: StreamingDataPoint) -> Dict[str, Any]:
        """Detect violations of biological constraints."""
        
        results = {
            'detected': False,
            'max_score': 0.0,
            'violations': {}
        }
        
        for key, value in data_point.values.items():
            if isinstance(value, (int, float)) and not np.isnan(value):
                
                # Check against biological bounds
                for constraint_key, (min_val, max_val) in self.biological_bounds.items():
                    if constraint_key in key.lower():
                        violation_score = 0.0
                        
                        if value < min_val:
                            violation_score = (min_val - value) / min_val
                        elif value > max_val:
                            violation_score = (value - max_val) / max_val
                        
                        if violation_score > 0:
                            results['detected'] = True
                            results['max_score'] = max(results['max_score'], min(violation_score, 1.0))
                            results['violations'][key] = {
                                'value': value,
                                'constraint': constraint_key,
                                'bounds': (min_val, max_val),
                                'violation_score': violation_score
                            }
                            break
                
                # Specific biological logic checks
                if 'fitness' in key.lower() and 'diversity' in data_point.values:
                    diversity = data_point.values.get('diversity', 0.5)
                    if isinstance(diversity, (int, float)):
                        # High fitness should not coexist with very high diversity
                        if value > 0.8 and diversity > 0.8:
                            results['detected'] = True
                            results['max_score'] = max(results['max_score'], 0.7)
                            results['violations']['fitness_diversity_inconsistency'] = {
                                'fitness': value,
                                'diversity': diversity,
                                'violation_score': 0.7
                            }
        
        return results
    
    def _detect_temporal_anomalies(self, data_point: StreamingDataPoint) -> Dict[str, Any]:
        """Detect temporal anomalies based on recent history."""
        
        results = {
            'detected': False,
            'max_score': 0.0,
            'temporal_issues': {}
        }
        
        if len(self.data_buffer) < 5:
            return results  # Need history for temporal analysis
        
        # Get recent data points
        recent_points = list(self.data_buffer)[-5:]
        
        for key, value in data_point.values.items():
            if isinstance(value, (int, float)) and not np.isnan(value):
                
                # Extract recent values for this key
                recent_values = []
                for point in recent_points:
                    if key in point.values:
                        recent_val = point.values[key]
                        if isinstance(recent_val, (int, float)) and not np.isnan(recent_val):
                            recent_values.append(recent_val)
                
                if len(recent_values) >= 3:
                    # Check for sudden jumps
                    mean_recent = np.mean(recent_values)
                    std_recent = np.std(recent_values)
                    
                    if std_recent > 0:
                        jump_score = abs(value - mean_recent) / std_recent
                        
                        if jump_score > 2.0:  # More than 2 standard deviations
                            results['detected'] = True
                            results['max_score'] = max(results['max_score'], min(jump_score / 4.0, 1.0))
                            results['temporal_issues'][key] = {
                                'current_value': value,
                                'recent_mean': mean_recent,
                                'recent_std': std_recent,
                                'jump_score': jump_score
                            }
                    
                    # Check for monotonic trends that are biologically implausible
                    if len(recent_values) >= 4:
                        is_monotonic_increasing = all(
                            recent_values[i] <= recent_values[i+1] 
                            for i in range(len(recent_values)-1)
                        )
                        is_monotonic_decreasing = all(
                            recent_values[i] >= recent_values[i+1] 
                            for i in range(len(recent_values)-1)
                        )
                        
                        # Check if monotonic trend is biologically implausible
                        if 'fitness' in key.lower():
                            if is_monotonic_increasing and value > 0.95:
                                # Fitness can't keep increasing indefinitely
                                results['detected'] = True
                                results['max_score'] = max(results['max_score'], 0.6)
                                results['temporal_issues'][f'{key}_unrealistic_trend'] = {
                                    'trend': 'monotonic_increasing',
                                    'current_value': value,
                                    'implausibility_score': 0.6
                                }
        
        return results
    
    def _record_anomaly(self, data_point: StreamingDataPoint, anomaly_results: Dict[str, Any]):
        """Record detected anomaly for analysis."""
        
        anomaly_record = {
            'data_id': data_point.data_id,
            'timestamp': data_point.timestamp,
            'data_type': data_point.data_type.name,
            'anomaly_score': anomaly_results['anomaly_score'],
            'anomaly_types': anomaly_results['anomaly_types'],
            'values': data_point.values.copy(),
            'detection_timestamp': time.time()
        }
        
        self.anomaly_history.append(anomaly_record)
        
        # Keep only recent anomalies
        if len(self.anomaly_history) > 1000:
            self.anomaly_history = self.anomaly_history[-500:]
    
    def get_anomaly_statistics(self) -> Dict[str, Any]:
        """Get statistics about detected anomalies."""
        
        if not self.anomaly_history:
            return {'message': 'No anomalies detected yet'}
        
        # Anomaly rate by type
        type_counts = defaultdict(int)
        for anomaly in self.anomaly_history:
            for anomaly_type in anomaly['anomaly_types']:
                type_counts[anomaly_type] += 1
        
        # Recent anomaly rate
        recent_time = time.time() - 3600  # Last hour
        recent_anomalies = [
            a for a in self.anomaly_history 
            if a['detection_timestamp'] > recent_time
        ]
        
        return {
            'total_anomalies': len(self.anomaly_history),
            'recent_anomalies_1h': len(recent_anomalies),
            'anomaly_rate_1h': len(recent_anomalies) / max(len(self.data_buffer), 1),
            'anomaly_types_distribution': dict(type_counts),
            'average_anomaly_score': np.mean([a['anomaly_score'] for a in self.anomaly_history]),
            'baseline_features': len(self.baseline_stats)
        }


class StreamProcessor:
    """
    Processes streaming data with adaptive batching.
    
    Patent Feature: Adaptive stream processing with
    biological knowledge-guided optimization.
    """
    
    def __init__(
        self,
        batch_size: int = 50,
        timeout: float = 5.0,
        update_strategy: UpdateStrategy = UpdateStrategy.ADAPTIVE
    ):
        """
        Initialize stream processor.
        
        Args:
            batch_size: Default batch size
            timeout: Batch timeout in seconds
            update_strategy: Strategy for processing updates
        """
        self.batch_size = batch_size
        self.timeout = timeout
        self.update_strategy = update_strategy
        
        # Processing queues
        self.input_queue: queue.Queue = queue.Queue()
        self.processing_batch: List[StreamingDataPoint] = []
        
        # Processing control
        self.is_processing = False
        self.processing_thread: Optional[threading.Thread] = None
        
        # Statistics
        self.processed_count = 0
        self.processing_times: List[float] = []
        self.batch_sizes: List[int] = []
        
        # Callbacks
        self.batch_processor: Optional[Callable] = None
        self.anomaly_callback: Optional[Callable] = None
        
        logger.info("Stream processor initialized")
    
    def set_batch_processor(self, processor: Callable[[List[StreamingDataPoint]], Any]):
        """Set callback for processing batches."""
        self.batch_processor = processor
    
    def set_anomaly_callback(self, callback: Callable[[StreamingDataPoint, Dict[str, Any]], None]):
        """Set callback for anomaly notifications."""
        self.anomaly_callback = callback
    
    def start_processing(self):
        """Start processing streaming data."""
        
        if self.is_processing:
            logger.warning("Stream processing already started")
            return
        
        self.is_processing = True
        self.processing_thread = threading.Thread(target=self._processing_loop)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        logger.info("Stream processing started")
    
    def stop_processing(self):
        """Stop processing streaming data."""
        
        self.is_processing = False
        
        if self.processing_thread:
            self.processing_thread.join(timeout=10.0)
        
        logger.info("Stream processing stopped")
    
    def add_data_point(self, data_point: StreamingDataPoint):
        """Add data point to processing queue."""
        
        if not self.is_processing:
            logger.warning("Stream processor not started, dropping data point")
            return
        
        try:
            self.input_queue.put(data_point, timeout=1.0)
        except queue.Full:
            logger.warning("Input queue full, dropping data point")
    
    def _processing_loop(self):
        """Main processing loop."""
        
        last_batch_time = time.time()
        
        while self.is_processing:
            try:
                # Get data point with timeout
                try:
                    data_point = self.input_queue.get(timeout=0.1)
                    self.processing_batch.append(data_point)
                except queue.Empty:
                    pass
                
                # Check if batch should be processed
                should_process = self._should_process_batch(last_batch_time)
                
                if should_process and self.processing_batch:
                    self._process_batch()
                    last_batch_time = time.time()
                
                # Adaptive batch size adjustment
                if self.update_strategy == UpdateStrategy.ADAPTIVE:
                    self._adjust_batch_parameters()
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                time.sleep(0.1)
        
        # Process remaining data
        if self.processing_batch:
            self._process_batch()
    
    def _should_process_batch(self, last_batch_time: float) -> bool:
        """Determine if batch should be processed."""
        
        current_time = time.time()
        
        if self.update_strategy == UpdateStrategy.IMMEDIATE:
            return len(self.processing_batch) >= 1
        
        elif self.update_strategy == UpdateStrategy.BATCHED:
            return len(self.processing_batch) >= self.batch_size
        
        elif self.update_strategy == UpdateStrategy.WINDOWED:
            return (current_time - last_batch_time) >= self.timeout
        
        elif self.update_strategy == UpdateStrategy.THRESHOLD_BASED:
            # Check if any high-priority or anomalous data points
            high_priority = any(
                point.is_anomaly or point.quality_score < 0.5 
                for point in self.processing_batch
            )
            return high_priority or len(self.processing_batch) >= self.batch_size
        
        elif self.update_strategy == UpdateStrategy.ADAPTIVE:
            # Adaptive logic: consider batch size, time, and data characteristics
            time_factor = (current_time - last_batch_time) / self.timeout
            size_factor = len(self.processing_batch) / self.batch_size
            
            # Priority factor based on data quality and anomalies
            priority_factor = 0.0
            if self.processing_batch:
                avg_quality = np.mean([p.quality_score for p in self.processing_batch])
                anomaly_count = sum(1 for p in self.processing_batch if p.is_anomaly)
                priority_factor = (1.0 - avg_quality) + (anomaly_count / len(self.processing_batch))
            
            # Adaptive threshold
            adaptive_threshold = 0.5 + 0.3 * priority_factor
            combined_factor = max(time_factor, size_factor) + 0.2 * priority_factor
            
            return combined_factor >= adaptive_threshold
        
        return False
    
    def _process_batch(self):
        """Process current batch of data points."""
        
        if not self.processing_batch:
            return
        
        start_time = time.time()
        batch_size = len(self.processing_batch)
        
        try:
            # Call batch processor if available
            if self.batch_processor:
                result = self.batch_processor(self.processing_batch)
                
                # Handle anomalies in the batch
                for point in self.processing_batch:
                    if point.is_anomaly and self.anomaly_callback:
                        try:
                            self.anomaly_callback(point, {'batch_result': result})
                        except Exception as e:
                            logger.error(f"Error in anomaly callback: {e}")
            
            # Mark as processed
            for point in self.processing_batch:
                point.processed = True
                point.processing_timestamp = time.time()
            
            # Update statistics
            processing_time = time.time() - start_time
            self.processed_count += batch_size
            self.processing_times.append(processing_time)
            self.batch_sizes.append(batch_size)
            
            # Keep only recent statistics
            if len(self.processing_times) > 100:
                self.processing_times = self.processing_times[-50:]
                self.batch_sizes = self.batch_sizes[-50:]
            
            logger.debug(f"Processed batch of {batch_size} items in {processing_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
        
        finally:
            self.processing_batch.clear()
    
    def _adjust_batch_parameters(self):
        """Adjust batch parameters based on performance."""
        
        if len(self.processing_times) < 10:
            return
        
        # Calculate recent performance metrics
        avg_processing_time = np.mean(self.processing_times[-10:])
        avg_batch_size = np.mean(self.batch_sizes[-10:])
        
        # Adjust batch size based on processing time
        if avg_processing_time > 1.0:  # Too slow
            self.batch_size = max(10, int(self.batch_size * 0.9))
        elif avg_processing_time < 0.1:  # Too fast
            self.batch_size = min(200, int(self.batch_size * 1.1))
        
        # Adjust timeout based on throughput
        target_throughput = 100  # data points per second
        current_throughput = avg_batch_size / (avg_processing_time + 1e-6)
        
        if current_throughput < target_throughput * 0.5:
            self.timeout = min(10.0, self.timeout * 1.2)
        elif current_throughput > target_throughput * 1.5:
            self.timeout = max(0.1, self.timeout * 0.8)
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processing performance statistics."""
        
        if not self.processing_times:
            return {'message': 'No processing performed yet'}
        
        avg_processing_time = np.mean(self.processing_times)
        avg_batch_size = np.mean(self.batch_sizes)
        
        return {
            'total_processed': self.processed_count,
            'average_processing_time': avg_processing_time,
            'average_batch_size': avg_batch_size,
            'current_batch_size': self.batch_size,
            'current_timeout': self.timeout,
            'processing_throughput': avg_batch_size / (avg_processing_time + 1e-6),
            'queue_size': self.input_queue.qsize(),
            'is_processing': self.is_processing,
            'update_strategy': self.update_strategy.name
        }


class RealTimeDataUpdater:
    """
    Main coordinator for real-time evolutionary data updates.
    
    Patent Feature: Comprehensive real-time data integration
    with anomaly detection and adaptive processing.
    """
    
    def __init__(
        self,
        update_strategy: UpdateStrategy = UpdateStrategy.ADAPTIVE,
        enable_anomaly_detection: bool = True
    ):
        """
        Initialize real-time data updater.
        
        Args:
            update_strategy: Strategy for processing updates
            enable_anomaly_detection: Whether to enable anomaly detection
        """
        self.update_strategy = update_strategy
        self.enable_anomaly_detection = enable_anomaly_detection
        
        # Components
        self.stream_processor = StreamProcessor(update_strategy=update_strategy)
        self.anomaly_detector = AnomalyDetector() if enable_anomaly_detection else None
        
        # Data management
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.data_history: deque = deque(maxlen=10000)
        
        # Event handlers
        self.update_callbacks: List[Callable] = []
        self.anomaly_callbacks: List[Callable] = []
        
        # Performance tracking
        self.update_statistics = {
            'total_updates': 0,
            'anomalies_detected': 0,
            'processing_errors': 0,
            'start_time': time.time()
        }
        
        # Set up stream processor callbacks
        self.stream_processor.set_batch_processor(self._process_data_batch)
        if self.anomaly_detector:
            self.stream_processor.set_anomaly_callback(self._handle_anomaly)
        
        logger.info("Real-time data updater initialized")
    
    def start(self):
        """Start real-time data processing."""
        
        self.stream_processor.start_processing()
        logger.info("Real-time data updater started")
    
    def stop(self):
        """Stop real-time data processing."""
        
        self.stream_processor.stop_processing()
        logger.info("Real-time data updater stopped")
    
    def add_update_callback(self, callback: Callable[[List[StreamingDataPoint]], None]):
        """Add callback for data updates."""
        self.update_callbacks.append(callback)
    
    def add_anomaly_callback(self, callback: Callable[[StreamingDataPoint, Dict[str, Any]], None]):
        """Add callback for anomaly alerts."""
        self.anomaly_callbacks.append(callback)
    
    def register_data_stream(
        self,
        stream_id: str,
        stream_config: Dict[str, Any]
    ):
        """Register a new data stream."""
        
        self.active_streams[stream_id] = {
            'config': stream_config,
            'registered_at': time.time(),
            'data_count': 0,
            'last_update': None
        }
        
        logger.info(f"Registered data stream: {stream_id}")
    
    def ingest_data_point(self, data_point: StreamingDataPoint):
        """
        Ingest a single data point for processing.
        
        Args:
            data_point: Streaming data point to process
        """
        
        # Pre-process data point
        processed_point = self._preprocess_data_point(data_point)
        
        # Anomaly detection
        if self.anomaly_detector:
            anomaly_results = self.anomaly_detector.detect_anomalies(processed_point)
            if anomaly_results['is_anomaly']:
                self.update_statistics['anomalies_detected'] += 1
        
        # Add to processing queue
        self.stream_processor.add_data_point(processed_point)
        
        # Update stream statistics
        if processed_point.stream_id in self.active_streams:
            self.active_streams[processed_point.stream_id]['data_count'] += 1
            self.active_streams[processed_point.stream_id]['last_update'] = time.time()
        
        # Add to history
        self.data_history.append(processed_point)
    
    def ingest_data_batch(self, data_points: List[StreamingDataPoint]):
        """
        Ingest a batch of data points.
        
        Args:
            data_points: List of streaming data points
        """
        
        for point in data_points:
            self.ingest_data_point(point)
    
    def _preprocess_data_point(self, data_point: StreamingDataPoint) -> StreamingDataPoint:
        """Preprocess data point before analysis."""
        
        # Validation
        if not data_point.data_id:
            data_point.data_id = f"auto_{int(time.time() * 1000000)}"
        
        # Quality assessment
        data_point.quality_score = self._assess_data_quality(data_point)
        
        # Confidence estimation
        data_point.confidence = self._estimate_confidence(data_point)
        
        return data_point
    
    def _assess_data_quality(self, data_point: StreamingDataPoint) -> float:
        """Assess quality of data point."""
        
        quality_factors = []
        
        # Completeness check
        expected_keys = self._get_expected_keys(data_point.data_type)
        if expected_keys:
            completeness = len(set(data_point.values.keys()) & set(expected_keys)) / len(expected_keys)
            quality_factors.append(completeness)
        
        # Value validity check
        valid_values = 0
        total_values = 0
        
        for key, value in data_point.values.items():
            total_values += 1
            if isinstance(value, (int, float)) and not np.isnan(value):
                # Check if value is in reasonable range
                if self._is_value_reasonable(key, value):
                    valid_values += 1
            elif isinstance(value, str) and len(value) > 0:
                valid_values += 1
        
        if total_values > 0:
            validity = valid_values / total_values
            quality_factors.append(validity)
        
        # Temporal consistency
        if hasattr(data_point, 'timestamp') and data_point.timestamp > 0:
            current_time = time.time()
            time_diff = abs(current_time - data_point.timestamp)
            temporal_quality = max(0.0, 1.0 - time_diff / 3600)  # Decay over 1 hour
            quality_factors.append(temporal_quality)
        
        # Overall quality score
        return np.mean(quality_factors) if quality_factors else 0.5
    
    def _estimate_confidence(self, data_point: StreamingDataPoint) -> float:
        """Estimate confidence in data point."""
        
        confidence_factors = []
        
        # Metadata-based confidence
        if 'measurement_error' in data_point.metadata:
            error = data_point.metadata['measurement_error']
            if isinstance(error, (int, float)) and error >= 0:
                confidence_factors.append(max(0.0, 1.0 - error))
        
        # Source reliability
        if 'source_reliability' in data_point.metadata:
            reliability = data_point.metadata['source_reliability']
            if isinstance(reliability, (int, float)):
                confidence_factors.append(np.clip(reliability, 0.0, 1.0))
        
        # Consensus with recent data
        if self.data_history:
            recent_similar = [
                p for p in list(self.data_history)[-20:] 
                if p.data_type == data_point.data_type and p.stream_id == data_point.stream_id
            ]
            
            if recent_similar:
                consensus_score = self._calculate_consensus(data_point, recent_similar)
                confidence_factors.append(consensus_score)
        
        return np.mean(confidence_factors) if confidence_factors else data_point.quality_score
    
    def _get_expected_keys(self, data_type: StreamingDataType) -> List[str]:
        """Get expected keys for a data type."""
        
        expected_keys_map = {
            StreamingDataType.REAL_TIME_SEQUENCING: ['sequence', 'quality_scores', 'read_count'],
            StreamingDataType.POPULATION_MONITORING: ['population_size', 'fitness', 'diversity'],
            StreamingDataType.ENVIRONMENTAL_SENSORS: ['temperature', 'ph', 'nutrient_levels'],
            StreamingDataType.PHENOTYPE_TRACKING: ['trait_values', 'measurement_timestamp'],
            StreamingDataType.EXPRESSION_PROFILING: ['gene_expression', 'gene_ids'],
            StreamingDataType.FITNESS_ASSAYS: ['fitness_value', 'assay_conditions'],
            StreamingDataType.DRUG_RESPONSES: ['drug_concentration', 'response_value'],
            StreamingDataType.METABOLIC_FLUX: ['flux_values', 'metabolite_ids']
        }
        
        return expected_keys_map.get(data_type, [])
    
    def _is_value_reasonable(self, key: str, value: Union[int, float]) -> bool:
        """Check if value is reasonable for the given key."""
        
        # Use biological bounds from anomaly detector
        if self.anomaly_detector:
            for constraint_key, (min_val, max_val) in self.anomaly_detector.biological_bounds.items():
                if constraint_key in key.lower():
                    return min_val <= value <= max_val
        
        # Default reasonableness checks
        if 'fitness' in key.lower():
            return 0.0 <= value <= 1.0
        elif 'population' in key.lower():
            return value >= 0
        elif 'temperature' in key.lower():
            return 200.0 <= value <= 400.0  # Kelvin
        elif 'ph' in key.lower():
            return 0.0 <= value <= 14.0
        
        return True  # Default: assume reasonable
    
    def _calculate_consensus(
        self, 
        data_point: StreamingDataPoint, 
        recent_points: List[StreamingDataPoint]
    ) -> float:
        """Calculate consensus score with recent data."""
        
        if not recent_points:
            return 0.5
        
        consensus_scores = []
        
        for key, value in data_point.values.items():
            if isinstance(value, (int, float)):
                recent_values = [
                    p.values.get(key) for p in recent_points
                    if key in p.values and isinstance(p.values[key], (int, float))
                ]
                
                if recent_values:
                    recent_mean = np.mean(recent_values)
                    recent_std = np.std(recent_values)
                    
                    if recent_std > 0:
                        # Consensus based on how close to recent mean
                        deviation = abs(value - recent_mean) / recent_std
                        consensus = max(0.0, 1.0 - deviation / 3.0)  # 3-sigma rule
                        consensus_scores.append(consensus)
                    else:
                        # All recent values are the same
                        consensus_scores.append(1.0 if value == recent_mean else 0.0)
        
        return np.mean(consensus_scores) if consensus_scores else 0.5
    
    def _process_data_batch(self, data_points: List[StreamingDataPoint]) -> Dict[str, Any]:
        """Process a batch of data points."""
        
        start_time = time.time()
        
        try:
            # Update statistics
            self.update_statistics['total_updates'] += len(data_points)
            
            # Group by data type for specialized processing
            grouped_data = defaultdict(list)
            for point in data_points:
                grouped_data[point.data_type].append(point)
            
            # Process each group
            processing_results = {}
            for data_type, points in grouped_data.items():
                type_results = self._process_data_type(data_type, points)
                processing_results[data_type.name] = type_results
            
            # Call update callbacks
            for callback in self.update_callbacks:
                try:
                    callback(data_points)
                except Exception as e:
                    logger.error(f"Error in update callback: {e}")
                    self.update_statistics['processing_errors'] += 1
            
            # Update anomaly detector baseline if enabled
            if self.anomaly_detector:
                normal_points = [p for p in data_points if not p.is_anomaly]
                if normal_points:
                    self.anomaly_detector.update_baseline(normal_points)
            
            processing_time = time.time() - start_time
            
            return {
                'processed_count': len(data_points),
                'processing_time': processing_time,
                'processing_results': processing_results,
                'anomaly_count': sum(1 for p in data_points if p.is_anomaly),
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error processing data batch: {e}")
            self.update_statistics['processing_errors'] += 1
            return {'error': str(e), 'processed_count': 0}
    
    def _process_data_type(
        self, 
        data_type: StreamingDataType, 
        points: List[StreamingDataPoint]
    ) -> Dict[str, Any]:
        """Process points of specific data type."""
        
        results = {
            'point_count': len(points),
            'data_type': data_type.name,
            'processing_timestamp': time.time()
        }
        
        if data_type == StreamingDataType.POPULATION_MONITORING:
            # Extract population metrics
            population_sizes = [
                p.values.get('population_size') for p in points
                if 'population_size' in p.values and isinstance(p.values['population_size'], (int, float))
            ]
            
            if population_sizes:
                results['population_stats'] = {
                    'mean': np.mean(population_sizes),
                    'std': np.std(population_sizes),
                    'min': np.min(population_sizes),
                    'max': np.max(population_sizes)
                }
        
        elif data_type == StreamingDataType.FITNESS_ASSAYS:
            # Extract fitness metrics
            fitness_values = [
                p.values.get('fitness_value') for p in points
                if 'fitness_value' in p.values and isinstance(p.values['fitness_value'], (int, float))
            ]
            
            if fitness_values:
                results['fitness_stats'] = {
                    'mean': np.mean(fitness_values),
                    'std': np.std(fitness_values),
                    'distribution': np.histogram(fitness_values, bins=10)[0].tolist()
                }
        
        # Add quality assessment
        quality_scores = [p.quality_score for p in points]
        results['quality_stats'] = {
            'mean_quality': np.mean(quality_scores),
            'min_quality': np.min(quality_scores),
            'high_quality_count': sum(1 for q in quality_scores if q > 0.8)
        }
        
        return results
    
    def _handle_anomaly(self, data_point: StreamingDataPoint, context: Dict[str, Any]):
        """Handle detected anomaly."""
        
        # Call anomaly callbacks
        for callback in self.anomaly_callbacks:
            try:
                callback(data_point, context)
            except Exception as e:
                logger.error(f"Error in anomaly callback: {e}")
        
        # Log anomaly
        logger.warning(
            f"Anomaly detected in {data_point.data_type.name}: "
            f"{data_point.data_id} at {data_point.timestamp}"
        )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        
        uptime = time.time() - self.update_statistics['start_time']
        
        status = {
            'uptime_seconds': uptime,
            'update_statistics': self.update_statistics.copy(),
            'active_streams': {
                stream_id: {
                    'data_count': info['data_count'],
                    'last_update': info['last_update'],
                    'uptime': uptime
                }
                for stream_id, info in self.active_streams.items()
            },
            'data_history_size': len(self.data_history),
            'processing_stats': self.stream_processor.get_processing_statistics(),
            'callbacks_registered': {
                'update_callbacks': len(self.update_callbacks),
                'anomaly_callbacks': len(self.anomaly_callbacks)
            }
        }
        
        # Add anomaly detection stats if enabled
        if self.anomaly_detector:
            status['anomaly_detection'] = self.anomaly_detector.get_anomaly_statistics()
        
        return status
    
    async def stream_websocket_data(self, websocket_url: str):
        """
        Stream data from WebSocket connection.
        
        Args:
            websocket_url: WebSocket URL to connect to
        """
        
        if not HAS_WEBSOCKET:
            logger.error("websocket-client library not available")
            return
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                data_point = StreamingDataPoint.from_dict(data)
                self.ingest_data_point(data_point)
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
        
        def on_error(ws, error):
            logger.error(f"WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            logger.info("WebSocket connection closed")
        
        def on_open(ws):
            logger.info("WebSocket connection opened")
        
        try:
            ws = websocket.WebSocketApp(
                websocket_url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            ws.run_forever()
            
        except Exception as e:
            logger.error(f"Error setting up WebSocket connection: {e}")
    
    def setup_redis_stream(self, redis_config: Dict[str, Any]):
        """
        Set up Redis stream for data ingestion.
        
        Args:
            redis_config: Redis configuration
        """
        
        if not HAS_REDIS:
            logger.error("redis library not available")
            return
        
        try:
            redis_client = redis.Redis(**redis_config)
            
            def stream_reader():
                while self.stream_processor.is_processing:
                    try:
                        # Read from Redis stream
                        messages = redis_client.xread(
                            {'evosphere_stream': '$'}, 
                            count=10, 
                            block=1000
                        )
                        
                        for stream_name, stream_messages in messages:
                            for message_id, fields in stream_messages:
                                try:
                                    # Convert Redis fields to data point
                                    data = {k.decode(): v.decode() for k, v in fields.items()}
                                    data_point = StreamingDataPoint.from_dict(data)
                                    self.ingest_data_point(data_point)
                                    
                                except Exception as e:
                                    logger.error(f"Error processing Redis message: {e}")
                    
                    except Exception as e:
                        logger.error(f"Error reading from Redis stream: {e}")
                        time.sleep(1)
            
            # Start stream reader in separate thread
            reader_thread = threading.Thread(target=stream_reader)
            reader_thread.daemon = True
            reader_thread.start()
            
            logger.info("Redis stream reader started")
            
        except Exception as e:
            logger.error(f"Error setting up Redis stream: {e}")
