def main():
    print("""
1.根据进程id查看端口
netstat -tulnp | grep 7126

2.根据端口查看相关进程
lsof -i:25000

3.排除文件名包含bak或log,排除bak目录和log目录，从sh脚本搜索文件
grep -rn --exclude-dir="*bak*" --exclude-dir="*log*" --exclude="*bak*" --exclude="*log*" --include="*.sh" "test.login_active_user_stable" *

""")

if __name__ == "__main__":
    main()