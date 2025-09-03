import argparse
import csv
import json
import sys
from .generator import DataGenerator

def main():
    parser = argparse.ArgumentParser(description="Generate random test data for testing and development.")
    
    # 添加数据类型选项
    parser.add_argument("--name", action="store_true", help="Generate random names")
    parser.add_argument("--email", action="store_true", help="Generate random email addresses")
    parser.add_argument("--date", action="store_true", help="Generate random dates")
    parser.add_argument("--int", dest="integer", action="store_true", help="Generate random integers")
    parser.add_argument("--float", action="store_true", help="Generate random floating-point numbers")
    parser.add_argument("--string", action="store_true", help="Generate random strings")
    parser.add_argument("--phone", action="store_true", help="Generate random phone numbers")
    parser.add_argument("--address", action="store_true", help="Generate random addresses")
    
    # 添加其他选项
    parser.add_argument("-n", "--number", type=int, default=1, help="Number of records to generate (default: 1)")
    parser.add_argument("-f", "--format", choices=["csv", "json"], default="csv", help="Output format (default: csv)")
    parser.add_argument("-o", "--output", help="Output file name (default: print to stdout)")
    parser.add_argument("--locale", default="en_US", help="Locale for localized data (e.g., zh_CN for Chinese)")
    
    args = parser.parse_args()
    
    # 如果没有指定任何数据类型，显示帮助信息
    if not any([args.name, args.email, args.date, args.integer, args.float, args.string, args.phone, args.address]):
        parser.print_help()
        return
    
    # 初始化生成器
    generator = DataGenerator(args.locale)
    
    # 确定要生成的数据类型
    selected_types = []
    if args.name:
        selected_types.append(('Name', generator.generate_name))
    if args.email:
        selected_types.append(('Email', generator.generate_email))
    if args.date:
        selected_types.append(('Date', generator.generate_date))
    if args.integer:
        selected_types.append(('Integer', generator.generate_int))
    if args.float:
        selected_types.append(('Float', lambda: generator.generate_float(0, 100, 2)))
    if args.string:
        selected_types.append(('String', lambda: generator.generate_string(10)))
    if args.phone:
        selected_types.append(('Phone', generator.generate_phone))
    if args.address:
        selected_types.append(('Address', generator.generate_address))
    
    # 生成数据
    data = []
    fieldnames = [name for name, _ in selected_types]
    
    for _ in range(args.number):
        record = {}
        for name, func in selected_types:
            record[name] = func()
        data.append(record)
    
    # 输出数据
    output_file = open(args.output, 'w', newline='', encoding='utf-8') if args.output else sys.stdout
    
    if args.format == 'csv':
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    elif args.format == 'json':
        json.dump(data, output_file, indent=2, ensure_ascii=False)
    
    if args.output:
        output_file.close()
        print(f"Data has been written to {args.output}")

if __name__ == "__main__":
    main()