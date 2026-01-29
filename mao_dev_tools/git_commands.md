# Git 常用命令速查


git add .
git commit -m "更新说明"
git push

## 🚀 初始配置

### 设置用户信息
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 查看配置
git config --list
git config user.name
git config user.email
```

### 配置编辑器
```bash
git config --global core.editor nano
git config --global core.editor vim
```

### 配置别名
```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.lg "log --oneline --graph --all"
```

## 📦 创建仓库

### 初始化仓库
```bash
git init                    # 在当前目录初始化
git init project-name       # 创建新目录并初始化
```

### 克隆仓库
```bash
git clone https://github.com/user/repo.git
git clone https://github.com/user/repo.git new-name
git clone git@github.com:user/repo.git     # SSH方式
```

## 📝 基本操作

### 查看状态
```bash
git status                  # 查看状态
git status -s               # 简短格式
git diff                    # 查看未暂存的修改
git diff --staged           # 查看已暂存的修改
git diff HEAD               # 查看所有修改
```

### 添加文件
```bash
git add file.txt            # 添加单个文件
git add .                   # 添加所有文件
git add *.py                # 添加所有.py文件
git add -A                  # 添加所有修改（包括删除）
git add -p                  # 交互式添加
```

### 提交
```bash
git commit -m "commit message"          # 提交
git commit -am "message"                # 添加并提交（已跟踪文件）
git commit --amend                      # 修改最后一次提交
git commit --amend -m "new message"     # 修改提交信息
```

### 撤销操作
```bash
git restore file.txt        # 撤销工作区修改
git restore --staged file.txt   # 取消暂存
git reset HEAD file.txt     # 取消暂存（旧方式）
git reset --soft HEAD~1     # 撤销最后一次提交（保留修改）
git reset --hard HEAD~1     # 撤销最后一次提交（丢弃修改）
git revert commit-hash      # 创建新提交来撤销指定提交
```

## 🌿 分支操作

### 查看分支
```bash
git branch                  # 查看本地分支
git branch -a               # 查看所有分支（包括远程）
git branch -r               # 查看远程分支
git branch -v               # 查看分支及最后一次提交
```

### 创建分支
```bash
git branch branch-name      # 创建分支
git checkout -b branch-name # 创建并切换到新分支
git switch -c branch-name   # 创建并切换（新命令）
```

### 切换分支
```bash
git checkout branch-name    # 切换分支
git switch branch-name      # 切换分支（新命令）
git checkout -              # 切换到上一个分支
```

### 合并分支
```bash
git merge branch-name       # 合并指定分支到当前分支
git merge --no-ff branch-name   # 禁用快进合并
git merge --squash branch-name  # 压缩合并
```

### 删除分支
```bash
git branch -d branch-name   # 删除已合并的分支
git branch -D branch-name   # 强制删除分支
git push origin --delete branch-name    # 删除远程分支
```

### 重命名分支
```bash
git branch -m old-name new-name     # 重命名分支
git branch -m new-name              # 重命名当前分支
```

## 🔄 远程仓库

### 查看远程仓库
```bash
git remote                  # 查看远程仓库
git remote -v               # 查看远程仓库URL
git remote show origin      # 查看远程仓库详细信息
```

### 添加远程仓库
```bash
git remote add origin https://github.com/user/repo.git
git remote add upstream https://github.com/original/repo.git
```

### 修改远程仓库
```bash
git remote rename old-name new-name     # 重命名
git remote remove origin                # 删除
git remote set-url origin new-url       # 修改URL
```

### 拉取和推送
```bash
git fetch origin            # 获取远程更新
git pull origin main        # 拉取并合并
git pull --rebase origin main   # 拉取并变基
git push origin main        # 推送到远程
git push -u origin main     # 推送并设置上游
git push --force            # 强制推送（危险！）
git push --all              # 推送所有分支
git push --tags             # 推送所有标签
```

## 📜 查看历史

### 查看提交历史
```bash
git log                     # 查看提交历史
git log --oneline           # 单行显示
git log --graph             # 图形化显示
git log --all --graph --oneline     # 完整图形化
git log -n 5                # 显示最近5次提交
git log --since="2 weeks ago"       # 最近两周
git log --author="Name"     # 指定作者
git log --grep="keyword"    # 搜索提交信息
git log file.txt            # 查看文件历史
git log -p file.txt         # 查看文件修改详情
```

### 查看提交详情
```bash
git show commit-hash        # 查看提交详情
git show HEAD               # 查看最新提交
git show HEAD~2             # 查看倒数第3次提交
```

### 查看文件历史
```bash
git blame file.txt          # 查看每行的修改者
git log --follow file.txt   # 查看文件重命名历史
```

## 🏷️ 标签管理

### 创建标签
```bash
git tag v1.0.0              # 创建轻量标签
git tag -a v1.0.0 -m "version 1.0.0"    # 创建附注标签
git tag -a v1.0.0 commit-hash   # 给指定提交打标签
```

### 查看标签
```bash
git tag                     # 查看所有标签
git tag -l "v1.*"           # 查看匹配的标签
git show v1.0.0             # 查看标签详情
```

### 推送标签
```bash
git push origin v1.0.0      # 推送单个标签
git push origin --tags      # 推送所有标签
```

### 删除标签
```bash
git tag -d v1.0.0           # 删除本地标签
git push origin --delete v1.0.0     # 删除远程标签
```

## 🔍 搜索和查找

```bash
git grep "keyword"          # 在工作目录搜索
git grep "keyword" branch-name      # 在指定分支搜索
git log -S "keyword"        # 搜索添加/删除了关键词的提交
git log --all --full-history -- file.txt   # 查找已删除文件
```

## 🧹 清理和维护

### 清理未跟踪文件
```bash
git clean -n                # 预览要删除的文件
git clean -f                # 删除未跟踪文件
git clean -fd               # 删除未跟踪文件和目录
git clean -fx               # 删除未跟踪和忽略的文件
```

### 存储临时修改
```bash
git stash                   # 存储当前修改
git stash save "message"    # 存储并添加说明
git stash list              # 查看存储列表
git stash pop               # 恢复最新存储并删除
git stash apply             # 恢复最新存储但不删除
git stash apply stash@{2}   # 恢复指定存储
git stash drop stash@{0}    # 删除指定存储
git stash clear             # 清空所有存储
```

### 优化仓库
```bash
git gc                      # 垃圾回收
git fsck                    # 检查仓库完整性
git prune                   # 清理不可达对象
```

## 🔀 高级操作

### 变基（Rebase）
```bash
git rebase main             # 将当前分支变基到main
git rebase -i HEAD~3        # 交互式变基最近3次提交
git rebase --continue       # 继续变基
git rebase --abort          # 取消变基
```

### 拣选（Cherry-pick）
```bash
git cherry-pick commit-hash     # 应用指定提交
git cherry-pick commit1 commit2 # 应用多个提交
git cherry-pick --continue      # 继续拣选
git cherry-pick --abort         # 取消拣选
```

### 子模块
```bash
git submodule add https://github.com/user/repo.git path/to/submodule
git submodule init          # 初始化子模块
git submodule update        # 更新子模块
git submodule update --remote  # 更新到最新版本
git clone --recursive url   # 克隆包含子模块的仓库
```

## 📋 .gitignore

### 常用规则
```bash
# 忽略所有 .log 文件
*.log

# 忽略目录
node_modules/
__pycache__/

# 忽略特定文件
config.local.py

# 不忽略特定文件
!important.log

# 忽略所有 .txt，但不忽略 readme.txt
*.txt
!readme.txt
```

### 忽略已跟踪文件
```bash
git rm --cached file.txt    # 从仓库删除但保留本地
git rm -r --cached folder/  # 删除文件夹
```

## 🔧 实用技巧

### 查看简洁日志
```bash
git log --oneline --graph --all --decorate
# 或设置别名
git config --global alias.lg "log --oneline --graph --all --decorate"
git lg
```

### 比较分支
```bash
git diff branch1..branch2       # 比较两个分支
git diff branch1...branch2      # 比较分支分叉点
git log branch1..branch2        # 查看branch2有但branch1没有的提交
```

### 查找提交
```bash
git bisect start            # 开始二分查找
git bisect bad              # 标记当前版本为坏
git bisect good commit-hash # 标记某版本为好
git bisect reset            # 结束查找
```

### 临时保存工作
```bash
# 方法1：使用stash
git stash
git checkout other-branch
# 做其他工作
git checkout original-branch
git stash pop

# 方法2：创建临时分支
git checkout -b temp-branch
git add .
git commit -m "temp"
git checkout original-branch
```

## 🚨 紧急情况处理

### 撤销推送
```bash
# 方法1：revert（推荐）
git revert commit-hash
git push

# 方法2：reset（危险）
git reset --hard commit-hash
git push --force
```

### 恢复删除的文件
```bash
git checkout HEAD -- file.txt       # 恢复到最新版本
git checkout commit-hash -- file.txt    # 恢复到指定版本
```

### 恢复删除的分支
```bash
git reflog                  # 查看引用日志
git checkout -b branch-name commit-hash
```

### 修复错误的提交
```bash
# 修改最后一次提交
git commit --amend

# 修改历史提交
git rebase -i HEAD~3
# 将要修改的提交标记为 edit
# 修改文件
git add .
git commit --amend
git rebase --continue
```

## 🔐 SSH密钥配置

```bash
# 生成SSH密钥
ssh-keygen -t ed25519 -C "your.email@example.com"

# 查看公钥
cat ~/.ssh/id_ed25519.pub

# 测试连接
ssh -T git@github.com

# 添加到ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

## 📊 常用工作流

### 功能开发流程
```bash
# 1. 创建功能分支
git checkout -b feature/new-feature

# 2. 开发并提交
git add .
git commit -m "Add new feature"

# 3. 推送到远程
git push -u origin feature/new-feature

# 4. 合并到主分支
git checkout main
git pull origin main
git merge feature/new-feature
git push origin main

# 5. 删除功能分支
git branch -d feature/new-feature
git push origin --delete feature/new-feature
```

### 修复Bug流程
```bash
# 1. 创建修复分支
git checkout -b hotfix/bug-fix

# 2. 修复并提交
git add .
git commit -m "Fix bug"

# 3. 合并到主分支
git checkout main
git merge hotfix/bug-fix
git push origin main

# 4. 删除修复分支
git branch -d hotfix/bug-fix
```

### 同步Fork仓库
```bash
# 1. 添加上游仓库
git remote add upstream https://github.com/original/repo.git

# 2. 获取上游更新
git fetch upstream

# 3. 合并到本地
git checkout main
git merge upstream/main

# 4. 推送到自己的仓库
git push origin main
```

## 💡 最佳实践

### 提交信息规范
```bash
# 格式：<type>: <subject>

feat: 添加新功能
fix: 修复bug
docs: 更新文档
style: 代码格式调整
refactor: 重构代码
test: 添加测试
chore: 构建/工具变动

# 示例
git commit -m "feat: 添加用户登录功能"
git commit -m "fix: 修复登录页面显示问题"
git commit -m "docs: 更新README安装说明"
```

### 分支命名规范
```bash
feature/功能名称      # 新功能
bugfix/bug描述       # bug修复
hotfix/紧急修复      # 紧急修复
release/版本号       # 发布分支
```

### 常用别名配置
```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.lg "log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
```

## ⚠️ 危险命令（慎用）

```bash
git push --force            # 强制推送（会覆盖远程历史）
git reset --hard            # 硬重置（会丢失修改）
git clean -fdx              # 删除所有未跟踪文件
git rebase                  # 变基（会改变历史）
git filter-branch           # 过滤分支（会重写历史）
```

## 📚 学习资源

```bash
git help                    # Git帮助
git help command            # 查看命令帮助
git command --help          # 查看命令详细帮助
```

---

**提示**：
- 提交前先 `git status` 检查状态
- 推送前先 `git pull` 获取最新代码
- 重要操作前先创建备份分支
- 使用 `git log` 查看历史避免错误
- 不确定的操作先在测试仓库尝试
