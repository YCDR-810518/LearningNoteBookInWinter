# typora的下载&配置心得

## typora的下载&安装

### 下载
原版一个激活码支持三个设备，买一个89块（也可以去小黄鱼上买空位）[原版下载&购买链接](https://typoraio.cn/)
这是我找到一个比较好的[**Typora下载&安装激活教程**](https://zhuanlan.zhihu.com/p/1971144711982026882)

### 关于激活和安装

我尝试了**最新版**，**高功能版本和老版本**，其中最新版的激活过于复杂，且功能与高功能版本的相差不大，建议直接用**高功能版本**
**老版本**没有图床的功能！

## 图床的设置

### 尝试

* 我尝试使用了**PicGo**（设置GitHub仓库为图床），卡在了测试上传的步骤，且在高功能版本中测试图片上传功能时会引起设置崩溃（Typora白屏）

* 我重新根据[官方文档](https://support.typora.io/Upload-Image/#picgo-core-command-line-opensource)中对于图片上传的相关软件和设置的推荐,测试了**Upgit**这个开源图片上传软件，按照其说明的安装上后成功设置好了图床
	[Upgit开源仓库中文说明](https://github.com/pluveto/upgit/blob/main/docs/README.zh-CN.md)
	[Release v0.2.25](https://github.com/pluveto/upgit/releases/tag/v0.2.25)

### GitHub图床设置流程

<img src="C:\Users\Administrator\Desktop\yc\Gawr-Gura-PNG-Isolated-Photo.png" alt="Gawr-Gura-PNG-Isolated-Photo" style="zoom:25%;" />

这部分直接问AI即可

### 注意，我在挂了梯子（全局代理）的情况下使用CDN加速会出现问题，如果你也是这样，请记得把Upgit配置文件中的这几行注释掉

配置文件（要记得根据REAME把文件名改成下面这样！）

![image-20260202162829897](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/02/upgit_20260202_1770020909.png)

CDN加速的相关配置

![image-20260202162947922](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/02/upgit_20260202_1770020988.png)

在偏好设置中设置好，最后在这里测试上传一下即可

![image-20260202163143218](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/02/upgit_20260202_1770021103.png)
