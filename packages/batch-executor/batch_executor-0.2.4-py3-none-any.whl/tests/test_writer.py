"""
writer.py 的 pytest 测试文件
核心功能：基础写入、多格式支持、批量处理等
"""
import pytest
import json
import csv
import time
import threading
import random
from pathlib import Path
import tempfile
import shutil

from batch_executor.writer import (
    BatchWriter, WriteFormat,
    create_writer, write_data_sync
)


@pytest.fixture
def temp_dir():
    """创建临时目录用于测试"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_data():
    """生成测试数据"""
    return [
        {"id": i, "name": f"user_{i}", "score": random.randint(60, 100)}
        for i in range(20)
    ]


class TestBatchWriter:
    """BatchWriter 基础功能测试"""
    
    def test_jsonl_write(self, temp_dir, sample_data):
        """测试JSONL格式写入"""
        file_path = temp_dir / "test.jsonl"
        
        with create_writer(file_path, format_type="jsonl", batch_size=5) as writer:
            writer.write_many(sample_data)
            writer.flush()
        
        # 验证文件存在
        assert file_path.exists()
        
        # 验证内容
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) == len(sample_data)
            
            first_record = json.loads(lines[0])
            assert first_record["id"] == 0
            assert "name" in first_record
    
    def test_json_write(self, temp_dir, sample_data):
        """测试JSON格式写入"""
        file_path = temp_dir / "test.json"
        
        with create_writer(file_path, format_type="json", batch_size=10) as writer:
            writer.write_many(sample_data[:5])
            writer.flush()
        
        # 验证文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) == 5
            assert data[0]["id"] == 0
    
    def test_csv_write(self, temp_dir):
        """测试CSV格式写入"""
        file_path = temp_dir / "test.csv"
        csv_data = [
            {"name": "Alice", "age": 25, "city": "Beijing"},
            {"name": "Bob", "age": 30, "city": "Shanghai"},
            {"name": "Carol", "age": 28, "city": "Guangzhou"},
        ]
        
        with create_writer(file_path, format_type="csv", batch_size=2) as writer:
            writer.write_many(csv_data)
            writer.flush()
        
        # 验证CSV内容
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 3
            assert rows[0]["name"] == "Alice"
            assert rows[0]["age"] == "25"
    
    def test_txt_write(self, temp_dir):
        """测试TXT格式写入"""
        file_path = temp_dir / "test.txt"
        text_data = ["line 1", "line 2", "line 3"]
        
        with create_writer(file_path, format_type="txt", batch_size=2) as writer:
            writer.write_many(text_data)
            writer.flush()
        
        # 验证文本内容
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.read().strip().split('\n')
            assert lines == text_data
    
    def test_batch_processing_with_sufficient_data(self, temp_dir, sample_data):
        """测试批量处理机制 - 使用足够的数据量"""
        file_path = temp_dir / "batch_test.jsonl"
        
        # 使用较小的批量大小和足够的数据量
        with create_writer(file_path, batch_size=3, flush_interval=0.5) as writer:
            # 写入足够触发批量写入的数据
            writer.write_many(sample_data[:10])
            
            # 等待批量写入完成
            time.sleep(1.0)
            
            # 强制刷新确保所有数据写入
            success = writer.flush(timeout=3.0)
            assert success
        
        # 验证文件有内容
        assert file_path.exists()
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 10
    
    def test_immediate_write_mode(self, temp_dir, sample_data):
        """测试立即写入模式（批量大小为1）"""
        file_path = temp_dir / "immediate_test.jsonl"
        
        with create_writer(file_path, batch_size=1, flush_interval=0.1) as writer:
            # 写入几条数据
            for item in sample_data[:3]:
                writer.write(item)
            
            # 短暂等待写入完成
            time.sleep(0.5)
        
        # 验证数据已写入
        assert file_path.exists()
        with open(file_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 3
    
    def test_auto_create_directory(self, temp_dir):
        """测试自动创建目录"""
        file_path = temp_dir / "subdir" / "deep" / "test.jsonl"
        
        with create_writer(file_path, auto_create_dir=True, batch_size=1) as writer:
            writer.write({"test": "data"})
            writer.flush()
        
        assert file_path.exists()
        assert file_path.parent.exists()


class TestErrorHandling:
    """错误处理测试"""
    
    def test_invalid_format(self, temp_dir):
        """测试无效格式处理"""
        with pytest.raises(ValueError):
            create_writer(temp_dir / "test.txt", format_type="invalid_format")
    
    def test_queue_full_handling(self, temp_dir):
        """测试队列满时的处理"""
        file_path = temp_dir / "queue_test.jsonl"
        
        # 创建小队列容量的写入器
        writer = BatchWriter(
            file_path, 
            WriteFormat.JSONL, 
            max_queue_size=3, 
            batch_size=20,  # 大批量，延迟写入
            flush_interval=10.0  # 长刷新间隔
        )
        writer.start()
        
        try:
            # 快速写入超过队列容量的数据，使用非阻塞模式
            results = []
            for i in range(8):
                result = writer.write({"id": i}, block=False, timeout=0.01)
                results.append(result)
            
            # 应该有一些写入失败（队列满）
            success_count = sum(1 for r in results if r)
            assert success_count < len(results), f"Expected some failures, but got {success_count}/{len(results)} successes"
            
        finally:
            writer.stop()
    
    def test_write_to_nonexistent_parent(self, temp_dir):
        """测试写入到不存在的父目录（auto_create_dir=False）"""
        file_path = temp_dir / "nonexistent" / "test.jsonl"
        
        # 不自动创建目录时应该处理错误
        writer = create_writer(file_path, auto_create_dir=False, batch_size=1)
        
        # 写入可能失败，但不应该崩溃
        result = writer.write({"test": "data"})
        writer.flush()
        writer.stop()


class TestConcurrency:
    """并发测试"""
    
    def test_concurrent_writes(self, temp_dir, sample_data):
        """测试并发写入"""
        file_path = temp_dir / "concurrent_test.jsonl"
        
        def write_worker(writer, data_slice, worker_id):
            """工作线程函数"""
            for item in data_slice:
                enhanced_item = {**item, "worker_id": worker_id}
                writer.write(enhanced_item)
        
        with create_writer(file_path, batch_size=3) as writer:
            # 创建2个线程同时写入
            threads = []
            chunk_size = len(sample_data) // 2
            
            for i in range(2):
                start_idx = i * chunk_size
                end_idx = start_idx + chunk_size if i < 1 else len(sample_data)
                data_slice = sample_data[start_idx:end_idx]
                
                thread = threading.Thread(
                    target=write_worker,
                    args=(writer, data_slice, i)
                )
                threads.append(thread)
                thread.start()
            
            # 等待所有线程完成
            for thread in threads:
                thread.join()
            
            writer.flush()
        
        # 验证数据被写入
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) == len(sample_data)
            
            # 验证有来自不同工作线程的数据
            worker_ids = set()
            for line in lines:
                record = json.loads(line)
                worker_ids.add(record["worker_id"])
            
            assert len(worker_ids) >= 2


class TestPerformance:
    """性能测试"""
    
    def test_batch_size_effect(self, temp_dir):
        """测试不同批量大小的效果"""
        test_data = [{"id": i, "data": "x" * 50} for i in range(50)]
        
        # 测试小批量
        file_path1 = temp_dir / "small_batch.jsonl"
        with create_writer(file_path1, batch_size=5) as writer:
            writer.write_many(test_data)
            writer.flush()
        
        # 测试大批量
        file_path2 = temp_dir / "large_batch.jsonl"
        with create_writer(file_path2, batch_size=25) as writer:
            writer.write_many(test_data)
            writer.flush()
        
        # 验证两个文件都正确写入
        assert file_path1.exists()
        assert file_path2.exists()
        
        # 验证内容数量相同
        with open(file_path1, 'r') as f1, open(file_path2, 'r') as f2:
            lines1 = f1.readlines()
            lines2 = f2.readlines()
            assert len(lines1) == len(lines2) == len(test_data)
    
    def test_stats_tracking(self, temp_dir, sample_data):
        """测试统计信息跟踪"""
        file_path = temp_dir / "stats_test.jsonl"
        
        with create_writer(file_path, batch_size=5) as writer:
            writer.write_many(sample_data[:15])
            writer.flush()
            
            stats = writer.get_stats()
            assert stats['total_written'] == 15
            assert stats['total_batches'] >= 3  # 15个项目，批量大小5，至少3个批次
            assert stats['errors'] == 0
            assert 'runtime' in stats
            assert stats['is_running']


class TestUtilityFunctions:
    """工具函数测试"""
    def test_write_data_sync(self, temp_dir, sample_data):
        """测试同步写入函数"""
        file_path = temp_dir / "sync_test.jsonl"
        
        result = write_data_sync(sample_data[:5], file_path, "jsonl")
        
        assert result is True
        assert file_path.exists()
        
        # 验证内容
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) == 5
    
    def test_create_writer_convenience(self, temp_dir):
        """测试便捷创建函数"""
        file_path = temp_dir / "convenience_test.jsonl"
        
        # 使用字符串格式类型
        writer = create_writer(file_path, "jsonl", batch_size=5)
        assert isinstance(writer, BatchWriter)
        assert writer.format_type == WriteFormat.JSONL
        
        writer.start()
        writer.write({"test": "data"})
        writer.flush()
        writer.stop()
        
        assert file_path.exists()


class TestContextManager:
    """上下文管理器测试"""
    
    def test_context_manager_basic(self, temp_dir, sample_data):
        """测试基础上下文管理器功能"""
        file_path = temp_dir / "context_test.jsonl"
        
        with create_writer(file_path, batch_size=5) as writer:
            writer.write_many(sample_data[:8])
            writer.flush()
            assert writer._is_running
        
        # 退出上下文后应该停止
        assert not writer._is_running
        assert file_path.exists()
    
    def test_context_manager_exception(self, temp_dir):
        """测试异常情况下的上下文管理器"""
        file_path = temp_dir / "exception_test.jsonl"
        
        try:
            with create_writer(file_path, batch_size=1) as writer:
                writer.write({"test": "data"})
                writer.flush()
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # 即使有异常，文件也应该被正确写入
        assert file_path.exists()


class TestEdgeCases:
    """边界情况测试"""
    
    def test_empty_data(self, temp_dir):
        """测试空数据处理"""
        file_path = temp_dir / "empty_test.jsonl"
        
        with create_writer(file_path, batch_size=5) as writer:
            writer.write_many([])
            writer.flush()
        
        # 空数据可能不会创建文件，这是正常的
        if file_path.exists():
            assert file_path.stat().st_size == 0
    
    def test_single_large_item(self, temp_dir):
        """测试大单项数据"""
        file_path = temp_dir / "large_item_test.jsonl"
        
        large_item = {"data": "x" * 5000, "id": 1}  # 5KB数据
        
        with create_writer(file_path, batch_size=1) as writer:
            writer.write(large_item)
            writer.flush()
        
        assert file_path.exists()
        
        # 验证内容
        with open(file_path, 'r', encoding='utf-8') as f:
            loaded_item = json.loads(f.readline())
            assert loaded_item["id"] == 1
            assert len(loaded_item["data"]) == 5000
    
    def test_special_characters(self, temp_dir):
        """测试特殊字符处理"""
        file_path = temp_dir / "special_chars_test.jsonl"
        
        special_data = [
            {"text": "Hello 世界", "id": 1},
            {"unicode": "ñáéíóú", "id": 2},
            {"symbols": "©®™", "id": 3},
        ]
        
        with create_writer(file_path, batch_size=2) as writer:
            writer.write_many(special_data)
            writer.flush()
        
        # 验证特殊字符正确保存
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) == 3
            
            first_item = json.loads(lines[0])
            assert "世界" in first_item["text"]
    
    def test_mixed_data_types(self, temp_dir):
        """测试混合数据类型"""
        file_path = temp_dir / "mixed_test.jsonl"
        
        mixed_data = [
            {"type": "dict", "value": {"nested": True}},
            {"type": "list", "value": [1, 2, 3]},
            {"type": "string", "value": "simple text"},
            {"type": "number", "value": 42},
            {"type": "boolean", "value": True},
        ]
        
        with create_writer(file_path, batch_size=3) as writer:
            writer.write_many(mixed_data)
            writer.flush()
        
        # 验证混合类型正确保存
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) == 5
            
            for i, line in enumerate(lines):
                item = json.loads(line)
                assert item["type"] == mixed_data[i]["type"]
                assert item["value"] == mixed_data[i]["value"]
    
    def test_flush_timeout(self, temp_dir):
        """测试刷新超时处理"""
        file_path = temp_dir / "flush_timeout_test.jsonl"
        
        with create_writer(file_path, batch_size=100, flush_interval=10.0) as writer:
            # 写入少量数据（不会触发批量写入）
            writer.write_many([{"id": i} for i in range(5)])
            
            # 测试短超时的刷新
            start_time = time.time()
            result = writer.flush(timeout=1.0)
            elapsed = time.time() - start_time
            
            # 刷新应该在超时时间内完成
            assert elapsed <= 2.0  # 给一些余量
            assert result is True  # 应该成功刷新
        
        # 验证数据被写入
        assert file_path.exists()
        with open(file_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 5
