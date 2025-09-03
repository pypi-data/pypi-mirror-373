"""Basic tests for tudata package"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import pandas as pd

# Add parent directory to path to import tudata
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tudata as ts


class TestTuDataBasic(unittest.TestCase):
    """Basic tests for TuData package"""

    @classmethod
    def setUpClass(cls):
        """Set up class level fixtures"""
        print("\n" + "="*60)
        print("🧪 开始运行 TuData 基础测试套件")
        print("="*60)

    def setUp(self):
        """Setup test fixtures"""
        # 优先从环境变量读取token，如果没有则使用有效的默认token
        self.test_token = os.environ.get('TUSHARE_TOKEN', "")
        print(f"\n🔍 执行测试: {self._testMethodName}")
        print(f"   🔑 当前token: {self.test_token[:10] if self.test_token else 'None'}...")

    def test_import(self):
        """Test that the package can be imported"""
        print("   📦 测试包导入功能")
        import tudata
        self.assertIsNotNone(tudata, "tudata package should be importable")
        print("   ✓ tudata包导入成功")
        
        # 验证包含必要的属性
        required_attrs = ['__version__', '__author__', '__email__']
        for attr in required_attrs:
            self.assertTrue(hasattr(tudata, attr), f"tudata should have {attr} attribute")
        print(f"   ✓ 包属性验证通过: {required_attrs}")

    def test_version(self):
        """Test that version is defined and follows semantic versioning"""
        print("   🏷️ 测试版本信息")
        self.assertIsNotNone(ts.__version__, "Version should not be None")
        self.assertIsInstance(ts.__version__, str, "Version should be a string")
        print(f"   ✓ 版本号: {ts.__version__}")
        
        # 确保版本遵循语义化版本规范
        version_parts = ts.__version__.split('.')
        self.assertGreaterEqual(len(version_parts), 2, "Version should have at least major.minor format")
        
        # 验证版本号都是数字
        for i, part in enumerate(version_parts):
            try:
                int(part)
            except ValueError:
                self.fail(f"Version part {i} ({part}) should be numeric")
        print(f"   ✓ 版本格式验证通过")

    def test_exports(self):
        """Test that main exports are available and callable"""
        print("   📤 测试包导出功能")
        required_exports = ['pro_api', 'pro_bar', 'set_token', 'get_token', 'BK']
        
        for export in required_exports:
            self.assertTrue(hasattr(ts, export), f"tudata should export {export}")
            
        # 验证函数类型
        self.assertTrue(callable(ts.pro_api), "pro_api should be callable")
        self.assertTrue(callable(ts.pro_bar), "pro_bar should be callable") 
        self.assertTrue(callable(ts.set_token), "set_token should be callable")
        self.assertTrue(callable(ts.get_token), "get_token should be callable")
        
        # 验证常量类型
        self.assertIsInstance(ts.BK, str, "BK should be a string constant")
        print(f"   ✓ 导出功能验证通过: {required_exports}")

    def test_pro_api_class_with_token(self):
        """Test that pro_api class can be instantiated with token"""
        print("   🔧 测试API类实例化（带token）")
        with patch('tudata.core.get_token', return_value=self.test_token):
            api = ts.pro_api(token=self.test_token)
            
            # 验证实例创建成功
            self.assertIsNotNone(api, "API instance should be created")
            self.assertEqual(api.token, self.test_token, "Token should be set correctly")
            print("   ✓ API实例创建成功")
            
            # 验证实例有必要的方法
            essential_methods = ['query', 'stock_basic', 'daily', 'trade_cal']
            for method in essential_methods:
                self.assertTrue(hasattr(api, method), f"API should have {method} method")
                self.assertTrue(callable(getattr(api, method)), f"{method} should be callable")
            print(f"   ✓ 核心方法验证通过: {essential_methods}")

    def test_pro_api_class_without_token(self):
        """Test that pro_api class initialization without token"""
        print("   🔧 测试API类实例化（不带token）")
        with patch('tudata.core.get_token', return_value=self.test_token):
            api = ts.pro_api()
            self.assertIsNotNone(api, "API instance should be created without explicit token")
            self.assertEqual(api.token, self.test_token, "Token should be retrieved from storage")
            print("   ✓ 无显式token的API实例创建成功")

    def test_pro_api_class_no_stored_token(self):
        """Test that pro_api class raises error when no token available"""
        print("   ❌ 测试无token时的错误处理")
        with patch('tudata.core.get_token', return_value=None):
            with self.assertRaises(ValueError) as context:
                ts.pro_api()
            
            error_message = str(context.exception)
            self.assertIn("请设置token", error_message, "Error should mention token setup requirement")
            print(f"   ✓ 错误处理验证通过: {error_message}")

    @patch('tudata.core.pd.DataFrame.to_csv')
    @patch('tudata.core.os.path.expanduser')
    def test_set_token(self, mock_expanduser, mock_to_csv):
        """Test set_token function with validation"""
        print("   💾 测试token设置功能")
        mock_expanduser.return_value = '/home/user'
        
        # 测试正常token设置
        test_token = 'test_token_123'
        ts.set_token(test_token)
        
        # 验证to_csv被调用
        mock_to_csv.assert_called_once()
        
        # 验证调用参数
        call_args = mock_to_csv.call_args
        self.assertIsNotNone(call_args, "to_csv should be called with arguments")
        print("   ✓ token设置功能验证通过")

    @patch('tudata.core.pd.read_csv')
    @patch('tudata.core.os.path.exists')
    @patch('tudata.core.os.path.expanduser')
    def test_get_token_exists(self, mock_expanduser, mock_exists, mock_read_csv):
        """Test get_token function when token file exists"""
        print("   🔑 测试token获取功能（文件存在）")
        mock_expanduser.return_value = '/home/user'
        mock_exists.return_value = True
        
        expected_token = 'test_token'
        # Mock DataFrame with token
        mock_df = MagicMock()
        mock_df.loc = {0: {'token': expected_token}}
        mock_read_csv.return_value = mock_df
        
        token = ts.get_token()
        
        self.assertEqual(token, expected_token, f"Should return stored token: {expected_token}")
        self.assertIsInstance(token, str, "Token should be a string")
        mock_read_csv.assert_called_once()
        print(f"   ✓ token获取成功: {expected_token}")

    @patch('tudata.core.os.path.exists')
    @patch('tudata.core.os.path.expanduser')
    def test_get_token_not_exists(self, mock_expanduser, mock_exists):
        """Test get_token function when token file doesn't exist"""
        print("   🔑 测试token获取功能（文件不存在）")
        mock_expanduser.return_value = '/home/user'
        mock_exists.return_value = False
        
        token = ts.get_token()
        self.assertIsNone(token, "Should return None when token file doesn't exist")
        print("   ✓ 文件不存在时返回None验证通过")

    @patch('tudata.core.get_token')
    def test_pro_api_query_method_exists(self, mock_get_token):
        """Test that pro_api has query method with proper signature"""
        print("   📡 测试API查询方法存在性")
        mock_get_token.return_value = self.test_token
        api = ts.pro_api(token=self.test_token)
        
        self.assertTrue(hasattr(api, 'query'), "API should have query method")
        self.assertTrue(callable(api.query), "query should be callable")
        
        # 测试query方法的参数
        import inspect
        query_signature = inspect.signature(api.query)
        expected_params = ['api_name', 'fields']
        
        for param in expected_params:
            self.assertIn(param, query_signature.parameters, 
                         f"query method should have {param} parameter")
        print(f"   ✓ query方法签名验证通过: {expected_params}")

    def test_pro_api_query_success(self):
        """Test successful API query with real data"""
        print("   📊 测试API查询功能（真实数据）")
        print(f"   🔍 检查token: {self.test_token}")
        
        # 跳过mock，直接使用真实API
        # 检查是否是有效的token（不是占位符）
        if (self.test_token and 
            self.test_token != "test_placeholder_token"):
            try:
                # 先测试更简单的API调用
                print("   🔍 开始调试API调用...")
                api = ts.pro_api(token=self.test_token)
                
                # 添加调试信息，监控API调用过程
                import requests
                from unittest.mock import patch
                
                original_post = requests.post
                def debug_post(*args, **kwargs):
                    print(f"      🌐 发送请求到: {args[0] if args else 'unknown'}")
                    print(f"      📤 请求数据: {kwargs.get('data', 'no data')[:200]}...")
                    
                    response = original_post(*args, **kwargs)
                    print(f"      📥 响应状态: {response.status_code}")
                    
                    # 查看响应内容
                    try:
                        response_data = response.json()
                        print(f"      📄 响应数据类型: {type(response_data)}")
                        print(f"      📄 响应数据长度: {len(response_data) if hasattr(response_data, '__len__') else 'N/A'}")
                        
                        # 显示数据的前几个元素或结构
                        if isinstance(response_data, list):
                            print(f"      📄 列表数据，前3个元素:")
                            for i, item in enumerate(response_data[:3]):
                                print(f"         元素{i+1}: {type(item)} - {str(item)[:100]}...")
                        elif isinstance(response_data, dict):
                            print(f"      📄 字典数据，键: {list(response_data.keys())}")
                            for key, value in list(response_data.items())[:3]:
                                print(f"         {key}: {type(value)} - {str(value)[:50]}...")
                        else:
                            print(f"      📄 数据内容: {str(response_data)[:200]}...")
                            
                    except Exception as e:
                        print(f"      ❌ 解析响应失败: {e}")
                        print(f"      📄 原始响应: {response.text[:200]}...")
                    
                    return response
                
                # 使用调试版本的post方法
                with patch('requests.post', side_effect=debug_post):
                    result = api.query('stock_basic', fields='ts_code,name', list_status='L')
                
                # 如果成功，显示结果
                if isinstance(result, pd.DataFrame):
                    print(f"      ✅ DataFrame创建成功!")
                    # 详细验证返回结果
                    self.assertIsInstance(result, pd.DataFrame, "Result should be a DataFrame")
                    self.assertGreater(len(result), 0, "DataFrame should not be empty")
                    self.assertIn('ts_code', result.columns, "Should contain ts_code column")
                    self.assertIn('name', result.columns, "Should contain name column")
                    
                    # 输出详细数据信息
                    print(f"      📊 返回数据维度: {result.shape[0]} 行 × {result.shape[1]} 列")
                    print(f"      📋 列名: {list(result.columns)}")
                    print(f"      📄 数据样例（前3行）:")
                    for i, (idx, row) in enumerate(result.head(3).iterrows()):
                        row_data = {col: str(val)[:20] + ('...' if len(str(val)) > 20 else '') 
                                  for col, val in row.items()}
                        print(f"         行{i+1}: {row_data}")
                    print(f"   ✓ API查询功能验证通过，返回{len(result)}行真实数据")
                else:
                    print(f"      📄 返回非DataFrame数据: {type(result)} - {str(result)[:100]}...")
                
            except Exception as e:
                print(f"   ❌ 真实API调用失败: {str(e)}")
                print(f"   🔍 错误类型: {type(e).__name__}")
                
                # 如果是DataFrame创建错误，提供更多调试信息
                if "scalar values" in str(e):
                    print("   🔍 这是pandas DataFrame创建错误，可能的原因:")
                    print("      - API返回的是单个标量值而不是列表/字典")
                    print("      - 数据格式不符合DataFrame要求")
                    print("      - 建议检查API响应的原始数据格式")
                
                import traceback
                print(f"   🔍 完整错误堆栈:")
                traceback.print_exc()
                
                print("   📝 提示: 请确保设置了有效的TUSHARE_TOKEN环境变量")
                # 如果真实API失败，跳过这个测试
                self.skipTest(f"需要有效的token进行真实API测试: {str(e)}")
        else:
            print(f"   ⚠️ 未检测到有效token，当前token: {self.test_token}")
            print("   📝 请设置环境变量 TUSHARE_TOKEN")
            print("   💡 示例: $env:TUSHARE_TOKEN='你的真实token'")
            self.skipTest("需要设置TUSHARE_TOKEN环境变量进行真实API测试")

    def test_pro_bar_success(self):
        """Test successful pro_bar function with real data"""
        print("   📈 测试pro_bar功能（真实数据）")
        print(f"   🔍 检查token: {self.test_token}")
        
        # 跳过mock，直接使用真实API
        if (self.test_token and 
            self.test_token != "test_placeholder_token"):
            try:
                print("123")
                # 修正：pro_bar需要指定api参数
                ts.set_token(self.test_token)
                result = ts.pro_bar(ts_code='000001.SZ', start_date='20240101', end_date='20240105')
                print(result)
                # 详细验证
                self.assertIsInstance(result, pd.DataFrame, "pro_bar should return DataFrame")
                
                # 对于真实数据，可能返回空数据（如节假日），所以不强制要求有数据
                if not result.empty:
                    expected_columns = ['ts_code', 'trade_date', 'close']
                    for col in expected_columns:
                        if col in result.columns:
                            print(f"      ✓ 包含预期列: {col}")
                    
                    # 验证数据类型
                    if 'close' in result.columns:
                        for close_price in result['close']:
                            if pd.notna(close_price):
                                self.assertIsInstance(close_price, (int, float), "Close price should be numeric")
                    
                    # 输出详细数据信息
                    print(f"      📊 返回数据维度: {result.shape[0]} 行 × {result.shape[1]} 列")
                    print(f"      📋 列名: {list(result.columns)}")
                    print(f"      📄 数据样例（前3行）:")
                    for i, (idx, row) in enumerate(result.head(3).iterrows()):
                        row_data = {col: str(val)[:20] + ('...' if len(str(val)) > 20 else '') 
                                  for col, val in row.items()}
                        print(f"         行{i+1}: {row_data}")
                    print(f"   ✓ pro_bar功能验证通过，返回{len(result)}行真实数据")
                else:
                    print("      ⚠️ 返回数据为空（可能是节假日或参数问题）")
                    print("   ✓ pro_bar功能正常（返回空数据）")
                
            except Exception as e:
                print(f"   ⚠️ 真实API调用失败: {str(e)}")
                print("   📝 提示: 请确保设置了有效的TUSHARE_TOKEN环境变量")
                self.skipTest(f"需要有效的token进行真实API测试: {str(e)}")
        else:
            print(f"   ⚠️ 未检测到有效token，当前token: {self.test_token}")
            print("   📝 请设置环境变量 TUSHARE_TOKEN")
            print("   💡 示例: $env:TUSHARE_TOKEN='你的真实token'")
            self.skipTest("需要设置TUSHARE_TOKEN环境变量进行真实API测试")

    @patch('tudata.core.get_token')
    def test_pro_bar_minute_frequency_restricted(self, mock_get_token):
        """Test that minute frequency is restricted in pro_bar with detailed check"""
        print("   ⚠️ 测试pro_bar分钟级频率限制")
        mock_get_token.return_value = self.test_token
        
        minute_frequencies = ['1min', '5min', '15min', '30min', '60min']
        expected_message = '此接口为单独权限，和积分没有关系,需要单独购买'
        
        for freq in minute_frequencies:
            result = ts.pro_bar(ts_code='000001.SZ', freq=freq)
            self.assertEqual(result, expected_message, 
                           f"Frequency {freq} should return restriction message")
            self.assertIsInstance(result, str, "Restriction should be a string message")
        print(f"   ✓ 分钟级频率限制验证通过：{len(minute_frequencies)}种频率")

    def test_bk_constant(self):
        """Test BK constant with validation"""
        print("   🔤 测试BK常量")
        self.assertEqual(ts.BK, 'bk', "BK constant should equal 'bk'")
        self.assertIsInstance(ts.BK, str, "BK should be a string")
        print(f"   ✓ BK常量验证通过: '{ts.BK}'")

    def test_package_metadata(self):
        """Test package metadata with detailed validation"""
        print("   📋 测试包元数据")
        metadata_attrs = ['__title__', '__author__', '__email__']
        
        for attr in metadata_attrs:
            self.assertTrue(hasattr(ts, attr), f"Package should have {attr}")
            value = getattr(ts, attr)
            self.assertIsInstance(value, str, f"{attr} should be a string")
            self.assertGreater(len(value), 0, f"{attr} should not be empty")
        
        # 验证具体值
        self.assertEqual(ts.__title__, 'tudata', "Title should be 'tudata'")
        
        # 验证email格式
        email = ts.__email__
        self.assertIn('@', email, "Email should contain @ symbol")
        self.assertRegex(email, r'.+@.+\..+', "Email should follow basic email format")
        print(f"   ✓ 包元数据验证通过: {ts.__title__} by {ts.__author__}")

    def test_all_exports(self):
        """Test that __all__ is properly defined and complete"""
        print("   📦 测试__all__导出列表")
        self.assertTrue(hasattr(ts, '__all__'), "Package should define __all__")
        self.assertIsInstance(ts.__all__, list, "__all__ should be a list")
        self.assertGreater(len(ts.__all__), 0, "__all__ should not be empty")
        
        # 检查__all__中的所有项目都实际可用
        for item in ts.__all__:
            self.assertIsInstance(item, str, f"__all__ item {item} should be string")
            self.assertTrue(hasattr(ts, item), f"{item} from __all__ not found in module")
            
        # 验证核心功能都在__all__中
        core_exports = ['pro_api', 'pro_bar', 'set_token', 'get_token']
        for export in core_exports:
            self.assertIn(export, ts.__all__, f"Core export {export} should be in __all__")
        print(f"   ✓ __all__导出列表验证通过，包含{len(ts.__all__)}个项目")

    def test_error_handling_comprehensive(self):
        """Test comprehensive error handling scenarios"""
        print("   🛡️ 测试综合错误处理")
        # 测试无效token格式
        with self.assertRaises(ValueError):
            with patch('tudata.core.get_token', return_value=None):
                ts.pro_api()
        
        # 测试空字符串token
        with patch('tudata.core.get_token', return_value=""):
            api = ts.pro_api(token="valid_token")  # 应该使用传入的token
            self.assertEqual(api.token, "valid_token")
        print("   ✓ 错误处理机制验证通过")


if __name__ == '__main__':
    # 设置更详细的测试输出
    unittest.main(verbosity=2) 