# Trajectory Tracking

<h1><b> Objective </b></h1>

In this project, we tackle a trajectory tracking problem for a differential-drive robot by employing two different approaches: Receding-Horizon Certainty Equivalent Control (CEC) and Generalized Policy Iteration (GPI). <br>

For the CEC controller, we utilize the CasADi solver, a symbolic Non Linear Programming solver, to design an optimal control policy that considers the dynamic constraints of the robot and the desired reference position trajectory. By solving the CEC problem, our aim is to achieve precise trajectory tracking and ensure that the robot accurately follows the desired path. <br>

In addition, we explore the Generalized Policy Iteration algorithm as an alternative approach for solving the trajectory tracking problem. With GPI, we iteratively refine and enhance the control policy based on observed outcomes and rewards, taking a Value Iteration approach. This allows us to explore alternative control strategies and improve the robot's trajectory tracking performance. <br>

The main objective of this project is to compare and evaluate the performance of the CEC and GPI approaches in trajectory tracking. Through thorough experimentation and analysis, we aim to gain insights into the strengths and weaknesses of each method and identify the most effective control policy for the differential-drive robot. By merging these two approaches, we aim to develop a robust and adaptive trajectory tracking system that can handle various scenarios and achieve accurate position tracking. This project contributes to the advancement of robotics by enhancing our understanding of trajectory tracking methods and their applicability in real-world scenarios. <br>

<p align="center">
  <img src="https://github.com/dhruvtalwar18/trajectory_tracking/blob/main/CEC/gifs/Q_20_10_5_10.gif" title="CEC Controller" style="width: 600px; height: 600px;">
  <br>
  <p align="center">Fig.1 CEC controller</p>
</p>



<h1><b> Code Setup </b></h1>
Clone the repository and install the requirements
```
git clone https://github.com/dhruvtalwar18/trajectory_tracking
cd trajectory_tracking
python3 -m venv venv
pip3 install -r requirements.txt
```

To run the CEC controller run the following:
```
python3 cec_controller.py
```

The script we have developed in this project serves the purpose of invoking our custom controller, whether it is the CEC or the Value Iteration obtained policy controller. Its main function is to simulate the robot's behavior as it strives to accurately follow a given reference trajectory.


To run the GPI algorithm run
```
python3 GPI_controller.py
```

In this script, we implement the Value Iteration algorithm to address the infinite horizon tracking problem. By running this algorithm, we aim to obtain the optimal policy function that guides the robot's actions in tracking the desired trajectory.







