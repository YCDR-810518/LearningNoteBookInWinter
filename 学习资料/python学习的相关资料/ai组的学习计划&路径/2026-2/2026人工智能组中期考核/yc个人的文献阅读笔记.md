# Differentially Private Formation Control: Privacy and Network Co-Design

> 作者：Calvin Hawkins, Matthew Hale
> 机构：

## 研究问题 Research Question

### 科学问题 Science Question

如何在保护轨迹隐私的同时减小其对编队带来的干扰？

### 推导过程

* 隐私如何带来干扰？

  * 共识算法

    * $$
      x 
      i
      ​	
       (k+1)=x 
      i
      ​	
       (k)+γ 
      j∈N 
      i
      ​	
       
      ∑
      ​	
       w 
      ij
      ​	
       (( 
      x
      ~
        
      j
      ​	
       (k)−Δ 
      j
      ​	
       )−(x 
      i
      ​	
       (k)−Δ 
      i
      ​	
       ))+n 
      i
      ​	
       (k)
      $$

      △i指的是坐标的相对偏差

      n(k) **过程噪声**

      γ: 学习速率，就是一个控制收敛速度的东西，数值越大，收敛的速度越大，但是存在让编队溃散的风险

  * 隐私带来的负面影响

    * 注意公式里的 **x~j**。根据我们之前的定义：
      $$
      x~j(k)=xj(k)+vj(k)
      $$
      把这个带入上面的更新方程，你会发现：
      $$
      xi(k+1)=正常编队项+γj∈Ni∑wijvj(k)+ni(k)
      $$

      * 因此，自己会接收邻居的噪声，扰乱自己的收敛动作
      * 误差会向图里传播，在图网络中传导

    

### 研究核心 Core of the research

#### 通过改善协同设计来维持编队稳定

通过**改变网络结构 wij** 来抵消噪声的影响

- **直观理解**：如果某个邻居的隐私需求特别高（噪声特别大），我们就调小和它通信的权重 wij，不那么听它的；同时增加其他“安静”邻居的权重，以此维持编队的稳定。

### 研究意义 Research significance



### 现有方法的不足 Shortcomings of existing algorithm



### 结论 Conclusion



---

## 理论与方法 Theory and Method



---

## 实验 Experiment



---

## 总结与思考 Summary and Reflections

