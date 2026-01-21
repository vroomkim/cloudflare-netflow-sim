<?php
$python_script = __DIR__ . '/netflow_sim.py';
$pid_file = __DIR__ . '/sim_process.pid';
$status = "Stopped";
$message = "";

function is_running($pid) {
    return file_exists("/proc/$pid");
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';
    if ($action === 'start') {
        $ip = escapeshellarg($_POST['ip']);
        $port = escapeshellarg($_POST['port']);
        $duration = escapeshellarg($_POST['duration']);
        $cmd = "nohup python3 $python_script --ip $ip --port $port --duration $duration > /dev/null 2>&1 & echo $!";
        $pid = shell_exec($cmd);
        file_put_contents($pid_file, trim($pid));
        $message = "Simulation started (PID: $pid)";
    } elseif ($action === 'stop') {
        if (file_exists($pid_file)) {
            $pid = file_get_contents($pid_file);
            exec("kill $pid");
            unlink($pid_file);
            $message = "Simulation stopped.";
        }
    }
}

if (file_exists($pid_file)) {
    $pid = trim(file_get_contents($pid_file));
    if (is_running($pid)) {
        $status = "<span style='color:green; font-weight:bold;'>RUNNING (PID: $pid)</span>";
    } else {
        $status = "<span style='color:red;'>Stopped (Stale PID)</span>";
        @unlink($pid_file);
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Cloudflare NetFlow Sim</title>
    <style>
        body { font-family: sans-serif; background: #f4f4f4; padding: 40px; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h2 { border-bottom: 2px solid #eee; padding-bottom: 10px; }
        label { display: block; margin-top: 15px; font-weight: bold; }
        input { width: 100%; padding: 8px; margin-top: 5px; }
        .btn-group { margin-top: 25px; display: flex; gap: 10px; }
        button { padding: 10px 20px; cursor: pointer; }
        .btn-start { background-color: #28a745; color: white; border: none; }
        .btn-stop { background-color: #dc3545; color: white; border: none; }
    </style>
</head>
<body>
<div class="container">
    <h2>NetFlow Generator</h2>
    <?php if ($message): ?><p style="background:#d4edda;padding:10px;"><?= htmlspecialchars($message) ?></p><?php endif; ?>
    <p>Status: <?= $status ?></p>
    <form method="POST">
        <label>Entry IP:</label><input type="text" name="ip" value="162.159.65.1" required>
        <label>Port:</label><input type="number" name="port" value="2055" required>
        <label>Duration (Min):</label><input type="number" name="duration" value="0" required>
        <div class="btn-group">
            <button type="submit" name="action" value="start" class="btn-start">Start</button>
            <button type="submit" name="action" value="stop" class="btn-stop">Stop</button>
        </div>
    </form>
</div>
</body>
</html>
