#!/usr/bin/env python3
"""
测试会话管理代码生成器的脚本
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 动态导入模块
import importlib.util
spec = importlib.util.spec_from_file_location("generator", "clean-arch-generator.py")
generator_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator_module)

CleanArchitectureGenerator = generator_module.CleanArchitectureGenerator

def test_session_management():
    """测试会话管理功能生成"""
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test-order-service"
        
        print("🧪 测试会话管理代码生成...")
        
        # 使用示例配置
        config = {
            'project': {
                'name': 'test-order-service',
                'version': '1.0.0',
                'language': 'go',
                'framework': 'clean-arch'
            },
            'aggregates': [
                {
                    'name': 'Order',
                    'fields': [
                        {'name': 'ID', 'type': 'string'},
                        {'name': 'CustomerID', 'type': 'string'},
                        {'name': 'Status', 'type': 'string'},
                        {'name': 'TotalAmount', 'type': 'float64'},
                        {'name': 'CreatedAt', 'type': 'time.Time'}
                    ]
                }
            ],
            'session': {
                'saga': {
                    'enabled': True,
                    'orchestration': 'orchestration',
                    'timeout': 300
                },
                'context': {
                    'storage': 'redis',
                    'ttl': 3600,
                    'prefix': 'test_session:'
                },
                'checkpoint': {
                    'enabled': True,
                    'interval': 30,
                    'strategy': 'time',
                    'max_retries': 3
                },
                'recovery': {
                    'enabled': True,
                    'strategy': 'compensate',
                    'max_attempts': 5,
                    'backoff': 'exponential'
                }
            },
            'long_running': {
                'enabled': True,
                'tasks': [
                    {
                        'name': 'order_processing',
                        'type': 'workflow',
                        'timeout': 1800,
                        'stages': [
                            {
                                'name': 'validate_order',
                                'service': 'order_service',
                                'endpoint': '/validate',
                                'timeout': 60
                            },
                            {
                                'name': 'process_payment',
                                'service': 'payment_service',
                                'endpoint': '/process',
                                'timeout': 120
                            }
                        ],
                        'compensation': [
                            {
                                'stage': 'process_payment',
                                'action': 'refund',
                                'service': 'payment_service'
                            }
                        ]
                    }
                ]
            }
        }
        
        # 创建生成器并生成代码
        generator = CleanArchitectureGenerator(
            project_name='test-order-service',
            config=config,
            base_path=str(project_path)
        )
        
        try:
            generator.generate()
            
            # 检查生成的文件
            expected_files = [
                'internal/infrastructure/session/config.go',
                'internal/infrastructure/session/manager.go', 
                'internal/infrastructure/session/saga.go',
                'internal/infrastructure/config/config.go',
                'configs/app.yaml',
                'docker-compose.yml'
            ]
            
            all_exist = True
            for file_path in expected_files:
                full_path = project_path / file_path
                if full_path.exists():
                    print(f"✅ {file_path}")
                else:
                    print(f"❌ {file_path}")
                    all_exist = False
            
            # 检查会话配置是否正确生成
            config_file = project_path / 'configs' / 'app.yaml'
            if config_file.exists():
                content = config_file.read_text()
                if 'session:' in content and 'long_running:' in content:
                    print("✅ 会话配置已正确生成")
                else:
                    print("❌ 会话配置未找到")
                    all_exist = False
            
            # 检查容器文件是否包含会话管理
            container_file = project_path / 'internal' / 'infrastructure' / 'container' / 'container.go'
            if container_file.exists():
                content = container_file.read_text()
                if 'SessionManager' in content and 'SagaManager' in content:
                    print("✅ 容器已集成会话管理")
                else:
                    print("❌ 容器未集成会话管理")
                    all_exist = False
            
            if all_exist:
                print("\n🎉 会话管理代码生成测试成功！")
                return True
            else:
                print("\n❌ 会话管理代码生成测试失败！")
                return False
                
        except Exception as e:
            print(f"❌ 生成过程中出错: {e}")
            return False

if __name__ == "__main__":
    success = test_session_management()
    sys.exit(0 if success else 1)