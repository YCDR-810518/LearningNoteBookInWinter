# git基本操作

## git commit操作

让所在的分支前进一步，相当于复制一份自己的东西

## git branch

分支操作，从主分支开出一条新分支时使用

1. git branch <分支名>

![image-20260317152808831](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/03/upgit_20260317_1773732489.png)	2. git checkout  <分支名>，要在**提交修改**前签出分支, 也可以用git switch <分支名>

![image-20260317153032997](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/03/upgit_20260317_1773732633.png)

## 分支&合并

### git merge

Git 中合并两个分支时会产生一个特殊的提交记录，它有两个 parent 节点。翻译成自然语言相当于：“我要把这两个 parent 节点本身及它们所有的祖先都包含进来。”

**将bugFix合并到main**

**git merge bugFix**

![image-20260317154008003](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/03/upgit_20260317_1773733208.png)

此时，main分支包含所有的提交记录，而bugFix不包含所有提交，我们可以在这时将**main合并到bugFix**

命令：**git checkout bugFix; git merge main**

![image-20260317154333322](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/03/upgit_20260317_1773733413.png)

### git rebase

移动以后会使得两个分支的功能看起来像是按顺序开发，但实际上它们是并行开发的。

注意，提交记录 C3 依然存在（树上那个半透明的节点），而 C3' 是我们 Rebase 到 main 分支上的 C3 的副本。

命令：**git rebase main**即将当前分支合并到main分支

![image-20260317155121262](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/03/upgit_20260317_1773733881.png)

## HEAD

HEAD 总是指向当前分支上最近一次提交记录。大多数修改提交树的 Git 命令都是从改变 HEAD 的指向开始的。

HEAD 通常情况下是指向分支名的（如 bugFix）。在你提交时，bugFix 的状态会被改变，且这一变化通过 HEAD 可见。

### 分离HEAD

**git check out <这里可以直接写要跳到的提交点>**

![image-20260317160442339](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/03/upgit_20260317_1773734682.png)

### HEAD相对引用的移动

首先看看操作符 `^`。把这个符号加在引用名称的后面，表示让 Git 寻找指定提交记录的 parent 提交。

所以 `main^` 相当于“`main` 的 parent 节点”。

`main^^` 是 `main` 的第二个 parent 节点

- 使用 `^` 向上移动 1 个提交记录
- 使用 `~<num>` 向上移动多个提交记录，如 `~3`

#### **一次后退多步**

**git switch HEAD~4**

![image-20260317162851602](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/03/upgit_20260317_1773736131.png)

#### 强制修改分支位置

命令：**git branch -f main HEAD~3**

这条命令会将 main 分支强制指向 HEAD 的往上数 3 级 parent 提交。

## 撤销变更Git Reset

`git reset` 通过将分支引用向后移动至一个更早的提交来撤销变更。从这个意义上说，你可以把它理解为“改写历史”。`git reset` 会把分支向上移动，就好像之前指向的提交从未发生过一样。

（在reset后， `C2` 所做的变更还在，但是处于未加入暂存区状态。）

命令：**git reset HEAD~1/HEAD^**

![image-20260317164028261](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/03/upgit_20260317_1773736828.png)

## 改写远程分支Git Revert

在我们要撤销的提交记录后面居然多了一个新提交！这是因为新提交记录 `C2'` 引入了**更改** —— 这些更改能够刚好撤销 `C2` 提交的变更。

命令：**git revert HEAD**

![image-20260317164238860](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/03/upgit_20260317_1773736959.png)

## cherry-pick神奇操作

我们想将 `side` 分支上的工作复制到 `main` 分支。这可以通过变基（即 rebase，我们已经学过了）来完成，但我们来看看 cherry-pick 是怎么做的。

命令：**git cherry-pick C2 C4**

![image-20260317164801731](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/03/upgit_20260317_1773737281.png)

## 交互式变基

当交互式变基对话框打开时，在我们的教学应用中，你可以做两件事：

- 调整提交记录的顺序（通过鼠标拖放来完成）
- 选择保留所有提交，或者丢弃特定的提交。当对话框打开时，每个提交旁边的 `pick` 按钮处于激活状态，表示该提交会被包含进来。要丢弃一个提交，只需关闭它的 `pick` 按钮。

命令：**git rebase -i HEAD~4**

起始：

![image-20260317170157535](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/03/upgit_20260317_1773738117.png)

输入命令后：**选择要丢弃的提交**

因为HEAD~4，所以会从C1开始变基

![image-20260317170243036](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/03/upgit_20260317_1773738163.png)

最终：

![image-20260317170434136](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/03/upgit_20260317_1773738274.png)
