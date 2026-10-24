$ErrorActionPreference = 'Stop'

# 通过 IPolicyConfig COM 接口把系统默认音频设备改回真实设备
# （VB-Cable 安装时会把自己设为默认，导致全系统声音被吸进虚拟声卡）

$cs = @'
using System;
using System.Runtime.InteropServices;

namespace AudioDef {
    [Guid("F8679F50-850A-41CF-9C72-430F290290C8"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IPolicyConfig {
        int GetMixFormat(IntPtr device, IntPtr format);
        int GetDeviceFormat(IntPtr device, int bDefault, IntPtr format);
        int ResetDeviceFormat(IntPtr device);
        int SetDeviceFormat(IntPtr device, IntPtr pFormat, IntPtr pOldFormat);
        int GetProcessingPeriod(IntPtr device, int bDefault, IntPtr defPeriod, IntPtr minPeriod);
        int SetProcessingPeriod(IntPtr device, IntPtr period);
        int GetShareMode(IntPtr device, IntPtr mode);
        int SetShareMode(IntPtr device, IntPtr mode);
        int GetPropertyValue(IntPtr device, int bFxStore, IntPtr key, IntPtr pv);
        int SetPropertyValue(IntPtr device, int bFxStore, IntPtr key, IntPtr pv);
        int SetDefaultEndpoint([MarshalAs(UnmanagedType.LPWStr)] string device, int role);
        int SetEndpointVisibility(IntPtr device, int bVisible);
    }

    [ComImport, Guid("870af99c-171d-4f9e-af0d-e63df40c2bc9")]
    class CPolicyConfigClient { }

    public static class Setter {
        public static int SetDefault(string endpointId, int role) {
            var cfg = (IPolicyConfig)(object)new CPolicyConfigClient();
            return cfg.SetDefaultEndpoint(endpointId, role);
        }
    }
}
'@
Add-Type -TypeDefinition $cs -Language CSharp

# 用 IMMDeviceEnumerator 枚举真实端点 ID（含全名，和系统声音设置里显示一致）
$cs2 = @'
using System;
using System.Runtime.InteropServices;

namespace AudioDef {
    [Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IMMDeviceEnumerator {
        int EnumAudioEndpoints(int dataFlow, int dwStateMask, out IMMDeviceCollection devices);
        int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice device);
        int GetDevice([MarshalAs(UnmanagedType.LPWStr)] string id, out IMMDevice device);
        int RegisterEndpointNotificationCallback(IntPtr pClient);
        int UnregisterEndpointNotificationCallback(IntPtr pClient);
    }

    [Guid("0BD7A1BE-7A1A-44DB-8397-CC5392387B5E"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IMMDeviceCollection {
        int GetCount(out int count);
        int Item(int nIndex, out IMMDevice device);
    }

    [Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IMMDevice {
        int Activate(ref Guid iid, int dwClsCtx, IntPtr pParams, out IntPtr iface);
        int OpenPropertyStore(int stgmAccess, out IPropertyStore store);
        int GetId([MarshalAs(UnmanagedType.LPWStr)] out string id);
        int GetState(out int state);
    }

    [Guid("886d8eeb-8cf2-4446-8d02-cdba1dbdcf99"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IPropertyStore {
        int GetCount(out int count);
        int GetAt(int prop, out PROPERTYKEY key);
        int GetValue(ref PROPERTYKEY key, out PROPVARIANT value);
        int SetValue(ref PROPERTYKEY key, ref PROPVARIANT value);
        int Commit();
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct PROPERTYKEY { public Guid fmtid; public int pid; }

    [StructLayout(LayoutKind.Sequential)]
    public struct PROPVARIANT {
        public ushort vt;
        public ushort r1, r2, r3;
        public IntPtr p;
    }

    public static class Tools {
        static readonly Guid CLSID_Enumerator = new Guid("BCDE0395-E52F-467C-8E3D-C4579291692E");
        static PROPERTYKEY PKEY_Name = new PROPERTYKEY {
            fmtid = new Guid("a45c254e-df1c-4efd-8020-67d146a850e0"), pid = 14 };

        public static string FindId(int flow, string contains) {
            var en = (IMMDeviceEnumerator)Activator.CreateInstance(
                Type.GetTypeFromCLSID(CLSID_Enumerator));
            IMMDeviceCollection col;
            en.EnumAudioEndpoints(flow, 1, out col);
            int n; col.GetCount(out n);
            for (int i = 0; i < n; i++) {
                IMMDevice dev; col.Item(i, out dev);
                string id; dev.GetId(out id);
                IPropertyStore store; dev.OpenPropertyStore(0, out store);
                PROPVARIANT pv; store.GetValue(ref PKEY_Name, out pv);
                string name = (pv.vt == 31 && pv.p != IntPtr.Zero)
                    ? Marshal.PtrToStringUni(pv.p) : "";
                if (name != null && name.ToLower().Contains(contains.ToLower())) return id + "|" + name;
            }
            return null;
        }
    }
}
'@
Add-Type -TypeDefinition $cs2 -Language CSharp

$playHit = [AudioDef.Tools]::FindId(0, 'HECATE')
$recHit  = [AudioDef.Tools]::FindId(1, '麦克风 (Realtek USB Audio)')

function Set-Role($id, $role, $label) {
    try {
        [void][AudioDef.Setter]::SetDefault($id, $role)
        Write-Output ("$label role=$role OK")
    } catch { Write-Output ("$label role=$role FAIL: " + $_.Exception.Message) }
}

if ($playHit) {
    $id, $name = $playHit -split '\|', 2
    Write-Output ("PLAYBACK: " + $name)
    0, 1, 2 | ForEach-Object { Set-Role $id $_ 'PLAYBACK' }
} else { Write-Output "NO_PLAYBACK_MATCH" }

if ($recHit) {
    $id, $name = $recHit -split '\|', 2
    Write-Output ("RECORDING: " + $name)
    0, 1, 2 | ForEach-Object { Set-Role $id $_ 'RECORDING' }
} else { Write-Output "NO_RECORDING_MATCH" }

# 播放: 找属性里含 HECATE 的活动端点（耳机 HECATE G1200）
# 录音: 找描述恰好是"麦克风"的活动端点（Realtek USB Audio 的麦克风；
#       "麦克风阵列"是网易虚拟设备、"CABLE Output"是虚拟声卡，都不匹配）
$play = Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Render' | ForEach-Object {
    $state = (Get-ItemProperty $_.PSPath -Name DeviceState -ErrorAction SilentlyContinue).DeviceState
    if ($state -ne 1) { return }
    $props = Get-ItemProperty (Join-Path $_.PSPath 'Properties') -ErrorAction SilentlyContinue
    $hit = $props.PSObject.Properties | Where-Object { $_.Value -is [string] -and $_.Value -match 'HECATE' } | Select-Object -First 1
    if ($hit) { [PSCustomObject]@{ Id = $_.PSChildName; Name = $hit.Value } }
} | Select-Object -First 1

$rec = Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Capture' | ForEach-Object {
    $state = (Get-ItemProperty $_.PSPath -Name DeviceState -ErrorAction SilentlyContinue).DeviceState
    if ($state -ne 1) { return }
    $props = Get-ItemProperty (Join-Path $_.PSPath 'Properties') -ErrorAction SilentlyContinue
    $desc = $props.'{a45c254e-df1c-4efd-8020-67d146a850e0},2'
    if ($desc -eq '麦克风') { [PSCustomObject]@{ Id = $_.PSChildName; Name = "$desc (Realtek USB Audio)" } }
} | Select-Object -First 1

if (-not $play) { Write-Output "NO_PLAYBACK_MATCH" }
if (-not $rec)  { Write-Output "NO_RECORDING_MATCH" }

foreach ($role in 0, 1, 2) {
    if ($play) {
        try {
            [void][AudioDef.Setter]::SetDefault('{0.0.0.00000000}.' + $play.Id, $role)
            Write-Output ("PLAYBACK role=$role OK -> " + $play.Name)
        } catch { Write-Output ("PLAYBACK role=$role FAIL: " + $_.Exception.Message) }
    }
    if ($rec) {
        try {
            [void][AudioDef.Setter]::SetDefault('{1.0.0.00000000}.' + $rec.Id, $role)
            Write-Output ("RECORDING role=$role OK -> " + $rec.Name)
        } catch { Write-Output ("RECORDING role=$role FAIL: " + $_.Exception.Message) }
    }
}
