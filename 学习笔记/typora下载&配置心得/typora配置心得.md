# typora的下载&配置心得

## typora的下载&安装

### 下载
原版一个激活码支持三个设备，买一个89块（也可以去小黄鱼上买空位）[原版下载&购买链接](https://typoraio.cn/)
这是我找到一个比较好的[**Typora下载&安装激活教程**](https://zhuanlan.zhihu.com/p/1971144711982026882)

### 关于激活和安装
我尝试了最新版，高功能版本和老版本，其中最新版的激活过于复杂，且功能与高功能版本的相差不大，建议直接用高功能版本
**老版本**没有图床的功能！

## 图床的设置

### 尝试

* 我尝试使用了**PicGo**（设置GitHub仓库为图床），卡在了测试上传的步骤，且在高功能版本中测试图片上传功能时会引起设置崩溃（Typora白屏）

* 我重新根据[官方文档](https://support.typora.io/Upload-Image/#picgo-core-command-line-opensource)中对于图片上传的相关软件和设置的推荐,测试了**Upgit**这个开源图片上传软件，按照其说明的安装上后成功设置好了图床
	[Upgit开源仓库中文说明](https://github.com/pluveto/upgit/blob/main/docs/README.zh-CN.md)
	[Release v0.2.25](https://github.com/pluveto/upgit/releases/tag/v0.2.25)

### GitHub图床设置流程
1. 要先在Github创建一个库作为上传的图床（**一定要设置为public否则会404**）
2. 点击settings
![6b78cf53-e3a5-4d10-833d-461d4daf2a59](https://cdn.jsdelivr.net/gh/YCDR-810518/imageBed/main/2026/02/upgit_20260202_1770019216.png)
3. 点击Developer settings
![3dc54118-d8bc-4a8a-a54c-f5607baf12a1](https://cdn.jsdelivr.net/gh/YCDR-810518/imageBed/main/2026/02/upgit_20260202_1770019462.png)
4. 再点这个传统token生成
![0f598904-4dc1-4bd2-a84b-0573fafb2ff9](https://cdn.jsdelivr.net/gh/YCDR-810518/imageBed/main/2026/02/upgit_20260202_1770019727.png)
