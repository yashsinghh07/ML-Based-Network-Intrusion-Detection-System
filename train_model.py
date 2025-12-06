import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# 1. Load NSL-KDD Dataset
columns = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes", "land",
    "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in", "num_compromised",
    "root_shell", "su_attempted", "num_root", "num_file_creations", "num_shells",
    "num_access_files", "num_outbound_cmds", "is_host_login", "is_guest_login", "count",
    "srv_count", "serror_rate", "srv_serror_rate", "rerror_rate", "srv_rerror_rate",
    "same_srv_rate", "diff_srv_rate", "srv_diff_host_rate", "dst_host_count",
    "dst_host_srv_count", "dst_host_same_srv_rate", "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate", "dst_host_serror_rate",
    "dst_host_srv_serror_rate", "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "label",
    "difficulty"
]

df = pd.read_csv("KDDTrain+.txt", names=columns)

# 2. Feature Selection
selected_features = ["protocol_type", "src_bytes", "dst_bytes"]
X = df[selected_features].copy()  # Use .copy() to avoid warnings
y = df['label'].apply(lambda x: 0 if x == 'normal' else 1)

# 3. Encode protocol_type
le_proto = LabelEncoder()
X['protocol_type'] = le_proto.fit_transform(X['protocol_type'])

# 4. Train Model
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X, y)

# 5. Save everything
joblib.dump(clf, 'nids_model.pkl')
joblib.dump(le_proto, 'le_proto.pkl')

print("✓ Model trained and saved!")
print(f"✓ Training Accuracy: {clf.score(X, y)*100:.2f}%")
print(f"✓ Features used: {selected_features}")
print(f"✓ Protocol classes: {list(le_proto.classes_)}")