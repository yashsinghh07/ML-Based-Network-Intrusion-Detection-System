Machine Learning–Based Real-Time Network Intrusion Detection System (NIDS)
==========================================================================

Project Overview
----------------
This project is a Machine Learning–based Real-Time Network Intrusion Detection System (NIDS) designed to identify and classify malicious network traffic in real time. It combines offline ML model training with real-time packet sniffing and a dashboard for live visualization.

The project uses Python, Scikit-learn, and Scapy for backend detection, and Streamlit for frontend visualization. The goal is to provide a simple but extendable architecture capable of evolving into a research-grade NIDS.

---------------------------------------------------------------------------
System Architecture
---------------------------------------------------------------------------
1. Data Sources:
   - Live packets captured from network interfaces (e.g., eth0).
   - Historical datasets such as NSL-KDD, CIC-IDS2017, and UNSW-NB15.

2. Data Capture Module:
   - Uses Scapy or PyShark to capture packets in real-time.

3. Feature Extraction Engine:
   - Extracts features like protocol type, packet size, source/destination bytes.
   - (Optional) Adds flow-based statistics for advanced detection.

4. ML Inference Engine:
   - Loads a pre-trained ML model (Random Forest or Deep Learning).
   - Classifies traffic as Normal or Attack.

5. Alerting and Logging System:
   - Logs results to alerts.log and nids_stats.txt.
   - Prints alerts in the console in real-time.

6. Visualization Dashboard:
   - Streamlit dashboard showing statistics and recent alerts.

---------------------------------------------------------------------------
7-Week Implementation Roadmap
---------------------------------------------------------------------------

Week 1: Foundations & Dataset Collection
- Study NIDS fundamentals.
- Download NSL-KDD, CIC-IDS2017, UNSW-NB15 datasets.
- Explore and visualize dataset distributions.
- Set up project environment and document data understanding.
Deliverables: Dataset exploration notebook, setup summary.

Week 2: Data Preprocessing & Feature Engineering
- Clean and preprocess datasets.
- Encode categorical data, normalize features.
- Handle class imbalance with SMOTE or undersampling.
- Select relevant features for training.
Deliverables: Preprocessing scripts, cleaned datasets.

Week 3: Model Selection and Offline Training
- Train baseline ML models: Random Forest, SVM, Logistic Regression, MLP.
- Evaluate using cross-validation.
- Select best-performing model.
Deliverables: Model training notebook, evaluation report.

Week 4: Real-Time Capture & Processing Pipeline
- Implement packet capture with Scapy.
- Extract live features and send to ML inference module.
- Log predictions in real time.
Deliverables: Working live_nids.py and test results.

Week 5: System Integration & Alerting
- Integrate all components (capture, inference, alert, logging).
- Create alerts for attacks and log data to files.
- Develop simple dashboard using Streamlit or Flask.
Deliverables: Fully integrated prototype, alerts.log, nids_stats.txt.

Week 6: Evaluation & Optimization
- Test accuracy, precision, recall, and F1-score on unseen data.
- Measure latency and throughput.
- Optimize model and code performance.
Deliverables: Final metrics report, optimized codebase.

Week 7: Enhancements & Deployment
- Implement deep learning models (LSTM/Autoencoder).
- Containerize with Docker and deploy.
- Add advanced visualization (Grafana/Dash).
- Prepare project report and documentation.
Deliverables: Docker setup, dashboard, final report.

---------------------------------------------------------------------------
Current Progress Summary (as of Dec 2025)
---------------------------------------------------------------------------

✅ Completed:
- Model training using Random Forest (train_model.py)
- Real-time inference engine using Scapy (live_nids.py)
- Alert logging (alerts.log)
- Detection statistics (nids_stats.txt)
- Base project fully functional locally

🔄 Pending / Next Steps:
- Add frontend dashboard visualization (Streamlit/Flask)
- Train deep learning models (LSTM/Autoencoder)
- Add advanced features and flow-based detection
- Optimize accuracy and latency
- Prepare final documentation and deployment setup

---------------------------------------------------------------------------
Project Structure
---------------------------------------------------------------------------
NIDS_Project/
│
├── src/
│   ├── train_model.py           (Offline training script)
│   ├── live_nids.py             (Real-time detection script)
│   └── train_deep_nids.py       (Optional deep learning script)
│
├── models/
│   ├── nids_model.pkl           (Random Forest model)
│   ├── le_proto.pkl             (Label encoder)
│   └── lstm_model.h5 (optional)
│
├── dashboard/
│   └── dashboard.py             (Streamlit dashboard)
│
├── logs/
│   ├── alerts.log               (Real-time alerts)
│   └── nids_stats.txt           (Traffic stats)
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── data/
│   └── KDDTrain+.txt
│
├── requirements.txt
└── README.txt

---------------------------------------------------------------------------
Installation & Setup
---------------------------------------------------------------------------

1. Clone the repository:
   git clone https://github.com/<your-username>/NIDS_Project.git
   cd NIDS_Project

2. Set up environment:
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

3. Train the model:
   python src/train_model.py

4. Run live detection:
   sudo python src/live_nids.py
   (sudo is required for network sniffing)

5. Start dashboard:
   streamlit run dashboard/dashboard.py

---------------------------------------------------------------------------
Key Features
---------------------------------------------------------------------------
- Offline ML training and model persistence
- Real-time packet capture and classification
- Logging and alerting with timestamps
- Dashboard visualization of traffic patterns
- Optional LSTM/Autoencoder for anomaly detection
- Docker deployment ready setup

---------------------------------------------------------------------------
Tools & Technologies
---------------------------------------------------------------------------
- Python 3.x
- Scikit-learn
- Scapy
- Pandas / NumPy
- Streamlit
- TensorFlow (optional)
- Docker / Docker Compose
- Grafana / Plotly (optional)

---------------------------------------------------------------------------
Testing & Simulation
---------------------------------------------------------------------------
To simulate attacks:
- Run an nmap scan: nmap -sS <YOUR_IP>
- Simulate a ping flood: ping -s 65000 <YOUR_IP>

The system will detect and log alerts for suspicious packets.

---------------------------------------------------------------------------
Future Enhancements
---------------------------------------------------------------------------
- Add flow-based feature extraction for accuracy.
- Integrate LSTM/Autoencoder-based detection.
- Build REST API for detection as a service.
- Visualize long-term traffic trends in Grafana.
- Cloud deployment via Docker or Kubernetes.

---------------------------------------------------------------------------
Contributors
---------------------------------------------------------------------------
- Yash Singh — Developer & Researcher

---------------------------------------------------------------------------
License
---------------------------------------------------------------------------
This project is licensed under the MIT License.

---------------------------------------------------------------------------
Quote
---------------------------------------------------------------------------
"Detecting intrusions in real time — one packet at a time."
