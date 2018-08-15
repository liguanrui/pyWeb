#### 关于本项目
初衷：年终总结里面说要自己纯手工 build 一个小型的 python-http-server 框架，该框架设想要满足以下一些基本内容

目前：经过一番折腾，还是完成得比较完善了，初衷的内容基本达标，也有一些遗憾点

#### 马上使用
```
# filetree
└─logic
    ├─basehttp                  // 轻量级 pyWebServer
    │   ├─modules               // 支持多个模块
    │   │   ├─base_controller   // 模块下的控制器
    │   │   ├─image_controller
    │   │   └─...
    │   ├─run.sh                // 守护进程脚本
    │   └─server.py             // 主要服务
    └─nginx2py                  // nginx + py 结合的 webServer
       └─...                    // 暂无开发

# shell
cd logic/basehttp
sh run.sh
```
#### 任务看板

##### 已完成
- [X] 可以处理基本的 GET 和 POST 请求
- [X] 拥有路由派发器，自动加载模块
- [X] 前后端分离，可作小型 rset
- [X] 基于 python2.7 版本的标准库（不依赖第三方库，方便使用）
- [X] 多线程处理，守护进程运行

##### 待开发
- [ ] cookie 处理
- [ ] request 与 response 有待优化
- [ ] upload 处理有待优化
- [ ] ab测试并发量到100会有问题
- [ ] 额外写一个配合nginx使用

#### 节点

- 1.0（2018-08-15）
