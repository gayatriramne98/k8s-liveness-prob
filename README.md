# 🚀 Kubernetes Liveness Probe Demo

A hands-on Kubernetes project demonstrating how **Liveness Probes** detect unhealthy containers and automatically restart them.

This project uses a lightweight **Flask application** with Kubernetes `httpGet` and `exec`-based liveness probes. It also demonstrates probe tuning, failure simulation, troubleshooting, and the difference between **Liveness** and **Readiness** probes.

---

## 📌 Project Overview

In Kubernetes, a container can be running but still be unhealthy due to application crashes, deadlocks, or other internal failures.

This project simulates such a failure using a Flask application.

The application provides:

* `/` — Application homepage
* `/healthz` — Health-check endpoint
* `/toggle` — Manually switches the application between healthy and unhealthy states

When `/healthz` starts returning **HTTP 500**, Kubernetes detects the failure through the configured liveness probe and automatically restarts the container.

---

## 🎯 Objectives

* Understand Kubernetes Liveness Probes.
* Configure an `httpGet` Liveness Probe.
* Configure an `exec`-based Liveness Probe.
* Simulate application health failures.
* Observe Kubernetes automatically restarting containers.
* Tune probe parameters.
* Troubleshoot probe failures using Kubernetes commands.
* Understand the difference between Liveness and Readiness Probes.

---

## 🏗️ Architecture

```text
                    ┌─────────────────────────┐
                    │       Kubernetes        │
                    │                         │
                    │   Deployment            │
                    │        │                │
                    │        ▼                │
                    │  ┌───────────────┐      │
                    │  │ Flask Pod     │      │
                    │  │               │      │
                    │  │ liveness-demo  │      │
                    │  │               │      │
                    │  │ /healthz      │◄─────┼── Liveness Probe
                    │  │ /toggle       │      │
                    │  └───────┬───────┘      │
                    │          │              │
                    │          ▼              │
                    │   Failed Health Check   │
                    │          │              │
                    │          ▼              │
                    │   Container Restart     │
                    └─────────────────────────┘
```

---

## 🛠️ Technologies Used

* **Kubernetes**
* **Docker**
* **Flask**
* **Python**
* **kubectl**
* **Docker Hub**

---

## 📂 Project Structure

```text
kubernetes-liveness-probe/
│
├── app/
│   ├── app.py
│   └── Dockerfile
│
├── deployment.yaml
├── deployment-exec-probe.yaml
└── README.md
```

---

## 🔍 Application Endpoints

| Endpoint   | Description                            |
| ---------- | -------------------------------------- |
| `/`        | Displays application information       |
| `/healthz` | Returns the current application health |
| `/toggle`  | Changes the application health state   |

### Healthy State

```text
/healthz → HTTP 200
```

### Unhealthy State

```text
/healthz → HTTP 500
```

The HTTP `500` response causes the Kubernetes liveness probe to fail.

---

# 🐳 1. Build the Docker Image

Navigate to the application directory:

```bash
cd app
```

Build the Docker image:

```bash
docker build -t <your-dockerhub-username>/liveness-demo:v1 .
```

Example:

```bash
docker build -t myusername/liveness-demo:v1 .
```

---

# 📤 2. Push Image to Docker Hub

Login to Docker Hub:

```bash
docker login
```

Push the image:

```bash
docker push <your-dockerhub-username>/liveness-demo:v1
```

Example:

```bash
docker push myusername/liveness-demo:v1
```

Update the image in `deployment.yaml`:

```yaml
image: <your-dockerhub-username>/liveness-demo:v1
```

---

# ☸️ 3. Deploy to Kubernetes

Apply the deployment:

```bash
kubectl apply -f deployment.yaml
```

Check the Deployment:

```bash
kubectl get deployments
```

Check the Pods:

```bash
kubectl get pods
```

Watch the Pod:

```bash
kubectl get pods -w
```

Initially, the Pod should be running with:

```text
READY   STATUS    RESTARTS
1/1     Running   0
```

---

# ❤️ 4. Test the Liveness Probe

Port-forward the Service:

```bash
kubectl port-forward svc/liveness-demo-svc 8080:80
```

Open another terminal.

Check application health:

```bash
curl http://localhost:8080/healthz
```

Expected:

```text
200
```

---

# 💥 5. Simulate an Application Failure

Use the `/toggle` endpoint:

```bash
curl http://localhost:8080/toggle
```

Check the health again:

```bash
curl http://localhost:8080/healthz
```

Expected:

```text
500
```

Now watch the Kubernetes Pod:

```bash
kubectl get pods -w
```

After the configured number of consecutive failures, Kubernetes will restart the container.

You should see the restart count increase:

```text
NAME                              READY   STATUS    RESTARTS
liveness-demo-xxxxxxxxxx-xxxxx    1/1     Running   1
```

---

# ⚙️ 6. Liveness Probe Configuration

Example configuration:

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 5000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 2
  failureThreshold: 3
  successThreshold: 1
```

### Probe Parameters

| Parameter             | Purpose                                          |
| --------------------- | ------------------------------------------------ |
| `initialDelaySeconds` | Delay before the first health check              |
| `periodSeconds`       | Time between health checks                       |
| `timeoutSeconds`      | Maximum time allowed for a response              |
| `failureThreshold`    | Consecutive failures before restart              |
| `successThreshold`    | Consecutive successes required to become healthy |

---

# ⏱️ 7. Tune Probe Timing

Modify:

```yaml
periodSeconds: 2
failureThreshold: 5
```

Apply the changes:

```bash
kubectl apply -f deployment.yaml
```

Restart the Deployment:

```bash
kubectl rollout restart deployment liveness-demo
```

Watch the Pod:

```bash
kubectl get pods -w
```

Approximate failure detection time:

```text
periodSeconds × failureThreshold

2 × 5 = 10 seconds
```

Previously:

```text
5 × 3 = 15 seconds
```

Therefore, the new configuration detects failures approximately **5 seconds faster**.

---

# 🧪 8. Intentionally Break the Probe

Change:

```yaml
path: /healthz
```

to:

```yaml
path: /wrong-path
```

Apply:

```bash
kubectl apply -f deployment.yaml
```

Watch the Pod:

```bash
kubectl get pods -w
```

The probe will continuously fail because `/wrong-path` does not exist.

Check the events:

```bash
kubectl describe pod <pod-name>
```

You should find events similar to:

```text
Liveness probe failed
```

and:

```text
Killing container ... failed liveness probe, will be restarted
```

This demonstrates how an incorrectly configured probe can cause unnecessary container restarts.

Restore the correct path:

```yaml
path: /healthz
```

Then re-apply the configuration.

---

# 🔧 9. Troubleshooting

### Describe the Pod

```bash
kubectl describe pod <pod-name>
```

### View Kubernetes Events

```bash
kubectl get events --sort-by=.lastTimestamp
```

### View Current Logs

```bash
kubectl logs <pod-name>
```

### View Previous Container Logs

```bash
kubectl logs <pod-name> --previous
```

The `--previous` option is especially useful after Kubernetes has restarted a container because it displays logs from the previous container instance.

---

# 🧩 10. Exec-Based Liveness Probe

The project also includes:

```text
deployment-exec-probe.yaml
```

Deploy it using:

```bash
kubectl apply -f deployment-exec-probe.yaml
```

An `exec` probe executes a command inside the container to determine whether the application is healthy.

Example:

```yaml
livenessProbe:
  exec:
    command:
      - sh
      - -c
      - <health-check-command>
```

### When to Use Exec Probes

Exec probes are useful when:

* An application does not expose an HTTP health endpoint.
* A background worker needs to be checked.
* A process needs to be verified.
* A lock file needs to be checked.
* An application-specific command can determine health.

For applications that already provide an HTTP health endpoint, `httpGet` is generally simpler.

---

# 🔄 11. Liveness vs Readiness

| Feature            | Liveness Probe                      | Readiness Probe                        |
| ------------------ | ----------------------------------- | -------------------------------------- |
| Purpose            | Checks whether container is healthy | Checks whether Pod can receive traffic |
| Failure action     | Container can be restarted          | Pod is removed from Service endpoints  |
| Restarts container | ✅ Yes                               | ❌ No                                   |
| Controls traffic   | ❌ No                                | ✅ Yes                                  |
| Typical use        | Detect deadlocks/crashes            | Startup or temporary unavailability    |

### Liveness

```text
Is the application still functioning?

        ↓

YES → Continue running

NO → Restart container
```

### Readiness

```text
Can the application receive traffic?

        ↓

YES → Send traffic

NO → Stop sending traffic
```

---

# 📊 12. Expected Result

After completing the project, the expected flow is:

```text
Flask Application
       │
       ▼
/healthz returns 200
       │
       ▼
Liveness Probe succeeds
       │
       ▼
Application becomes unhealthy
       │
       ▼
/healthz returns 500
       │
       ▼
Liveness Probe fails
       │
       ▼
Failure threshold reached
       │
       ▼
Kubernetes restarts container
       │
       ▼
Application becomes healthy again
```

---

# 🧹 13. Cleanup

Delete the main Deployment and Service:

```bash
kubectl delete -f deployment.yaml
```

Delete the exec-probe Deployment:

```bash
kubectl delete -f deployment-exec-probe.yaml
```

Verify:

```bash
kubectl get pods
kubectl get deployments
kubectl get services
```

---

# 📚 14. Key Learnings

Through this project, I learned how to:

* Configure Kubernetes Liveness Probes.
* Use HTTP health checks with `httpGet`.
* Use command-based health checks with `exec`.
* Simulate application failures.
* Observe Kubernetes automatic container restarts.
* Tune probe timing parameters.
* Diagnose failed health checks.
* Analyze Kubernetes events.
* Use `kubectl logs --previous`.
* Understand Liveness vs Readiness Probes.
* Troubleshoot incorrectly configured probes.

---

# 🚀 Future Improvements

Possible improvements to this project include:

* Add a Kubernetes `readinessProbe`.
* Add a `startupProbe`.
* Add Prometheus monitoring.
* Add Grafana dashboards.
* Deploy the application using Helm.
* Add CI/CD using Jenkins or GitHub Actions.
* Deploy the application to a cloud Kubernetes cluster.

---

# 👩‍💻 Author

**Gayatri Ramne**

B.Sc. Data Science | Cloud & DevOps Enthusiast

### Skills Demonstrated

`Linux` `Docker` `Kubernetes` `Python` `Flask` `kubectl` `DevOps` `Cloud`

---

## ⭐ Project Highlights

> This project demonstrates Kubernetes self-healing using Liveness Probes by intentionally simulating application health failures and observing Kubernetes automatically restart the unhealthy container.
