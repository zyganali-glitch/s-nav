using System;
using System.IO;
using System.Runtime.InteropServices;

internal static class Program
{
    private const uint SkdvSuccess = 0x00000000;
    private const uint SkdvDeviceStaMask = 0xFFFFFF80;
    private const uint SkdvDeviceStQ1 = 0x20028880;

    [StructLayout(LayoutKind.Sequential)]
    private struct SK_DV_SR3500MARK_CONF
    {
        public int iBackSideReading;
        public int iColumns;
        public int iReadingMethod;
        public int iCtrlMultiple;
        public int iThicknessType;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct SK_DV_MARK_INFO
    {
        public int iType;
        public int iRows;
        public int iColumns;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct SK_DV_MARK_SKEW
    {
        public int iRow;
        public int iLevel;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct SK_DV_BUZZER
    {
        public int iVol;
        public int iTone;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct SK_DV_PSAVING
    {
        public int iSleep;
        public int iStandby;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct SK_DV_SR3500_MODE
    {
        public int iFeedMode;
        public int iFeedTime;
        public uint dwDisableWarning;
        public SK_DV_MARK_SKEW MarkSkew;
        public int iPanelOperation;
        public SK_DV_BUZZER Buzzer;
        public SK_DV_PSAVING PSaving;
    }

    // Warning flags for dwDisableWarning (OR these in to SUPPRESS the error)
    private const uint SkdvWarnTmError  = 0x00040000; // Timing Mark error detection
    private const uint SkdvWarnDfError  = 0x00080000; // Double-feed detection
    private const uint SkdvWarnLeftSkew = 0x00100000; // Left edge skew detection

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool SetDllDirectory(string lpPathName);

    [DllImport("SkDvSr3500Img.dll", CallingConvention = CallingConvention.Winapi)]
    private static extern uint SkDv_OpenSingle(ref uint handle);

    [DllImport("SkDvSr3500Img.dll", CallingConvention = CallingConvention.Winapi)]
    private static extern uint SkDv_OpenWithOmrapi(ref uint handle);

    [DllImport("SkDvSr3500Img.dll", CallingConvention = CallingConvention.Winapi)]
    private static extern uint SkDv_ReqInit(uint handle);

    [DllImport("SkDvSr3500Img.dll", CallingConvention = CallingConvention.Winapi)]
    private static extern uint SkDv_GetMode(uint handle, ref SK_DV_SR3500_MODE mode);

    [DllImport("SkDvSr3500Img.dll", CallingConvention = CallingConvention.Winapi)]
    private static extern uint SkDv_SetMode(uint handle, ref SK_DV_SR3500_MODE mode);

    [DllImport("SkDvSr3500Img.dll", CallingConvention = CallingConvention.Winapi)]
    private static extern uint SkDv_GetMarkConf(uint handle, ref SK_DV_SR3500MARK_CONF markConf);

    [DllImport("SkDvSr3500Img.dll", CallingConvention = CallingConvention.Winapi)]
    private static extern uint SkDv_SetMarkConf(uint handle, ref SK_DV_SR3500MARK_CONF markConf);

    [DllImport("SkDvSr3500Img.dll", CallingConvention = CallingConvention.Winapi)]
    private static extern uint SkDv_ReqGetSensor(uint handle, ref uint sensorBits);

    [DllImport("SkDvSr3500Img.dll", CallingConvention = CallingConvention.Winapi)]
    private static extern uint SkDv_ReqFeedMarkSheet(uint handle);

    [DllImport("SkDvSr3500Img.dll", CallingConvention = CallingConvention.Winapi)]
    private static extern uint SkDv_ReqGetMarks(uint handle, int face, ref SK_DV_MARK_INFO markInfo, byte[] marks, ref int bufferSize);

    [DllImport("SkDvSr3500Img.dll", CallingConvention = CallingConvention.Winapi)]
    private static extern uint SkDv_Close(uint handle);

    [DllImport("SkDvSr3500Img.dll", CallingConvention = CallingConvention.Winapi)]
    private static extern uint SkDv_ReqEjectForm(uint handle, int iDirection);

    private const int SkdvEjectMain = 1; // Eject to Main Stacker (immediate)

    private static int Main(string[] args)
    {
        string sdkBin = args.Length > 0 && !string.IsNullOrWhiteSpace(args[0])
            ? args[0]
            : @"C:\SecureExam\vendor-media\English\English\API Library\Bin";
        string action = args.Length > 1 && !string.IsNullOrWhiteSpace(args[1])
            ? args[1]
            : "probe";
        string outputPath = args.Length > 2 && !string.IsNullOrWhiteSpace(args[2])
            ? args[2]
            : Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "last-mark-read.txt");
        int maxSheets = args.Length > 3 ? SafeParseInt(args[3], 0) : 0;
        int configuredColumns = args.Length > 4 ? SafeParseInt(args[4], 48) : 48;
        int configuredReadingMethod = args.Length > 5 ? SafeParseInt(args[5], 3) : 3;
        int configuredThicknessType = args.Length > 6 ? SafeParseInt(args[6], 0) : 0;
        bool configuredBackside = args.Length > 7 && SafeParseInt(args[7], 0) == 1;

        Console.WriteLine("sr3500_vendor_probe_x86 starting");
        Console.WriteLine("process_arch=" + (Environment.Is64BitProcess ? "x64" : "x86"));
        Console.WriteLine("sdk_bin=" + sdkBin);
        Console.WriteLine("action=" + action);

        if (!Directory.Exists(sdkBin))
        {
            Console.WriteLine("error=sdk_bin_missing");
            return 10;
        }

        string driverDll = Path.Combine(sdkBin, "SkDvSr3500Img.dll");
        if (!File.Exists(driverDll))
        {
            Console.WriteLine("error=driver_dll_missing");
            return 11;
        }

        if (!SetDllDirectory(sdkBin))
        {
            Console.WriteLine("warning=SetDllDirectory_failed win32=" + Marshal.GetLastWin32Error());
        }

        uint handle = 0;

        try
        {
            uint openStatus = SkDv_OpenSingle(ref handle);
            Console.WriteLine("open_single_status=0x" + openStatus.ToString("X8"));
            Console.WriteLine("handle=0x" + handle.ToString("X8"));

            if (openStatus != SkdvSuccess)
            {
                handle = 0;
                uint fallbackStatus = SkDv_OpenWithOmrapi(ref handle);
                Console.WriteLine("open_with_omrapi_status=0x" + fallbackStatus.ToString("X8"));
                Console.WriteLine("fallback_handle=0x" + handle.ToString("X8"));
                if (fallbackStatus != SkdvSuccess)
                {
                    return 20;
                }
            }

            uint initStatus = SkDv_ReqInit(handle);
            Console.WriteLine("req_init_status=0x" + initStatus.ToString("X8"));

            if (initStatus != SkdvSuccess)
            {
                uint failedCloseStatus = SkDv_Close(handle);
                Console.WriteLine("close_status=0x" + failedCloseStatus.ToString("X8"));
                return 21;
            }

            uint sensorBits = 0;
            uint sensorStatus = SkDv_ReqGetSensor(handle, ref sensorBits);
            Console.WriteLine("sensor_status=0x" + sensorStatus.ToString("X8"));
            Console.WriteLine("sensor_bits=0x" + sensorBits.ToString("X8"));

            if (string.Equals(action, "mark-once", StringComparison.OrdinalIgnoreCase))
            {
                int markReadResult = RunMarkRead(handle, outputPath, configuredColumns, configuredReadingMethod, configuredThicknessType, configuredBackside, 1);
                uint closeAfterMark = SkDv_Close(handle);
                Console.WriteLine("close_status=0x" + closeAfterMark.ToString("X8"));
                return markReadResult;
            }

            if (string.Equals(action, "mark-batch", StringComparison.OrdinalIgnoreCase))
            {
                int markReadResult = RunMarkRead(handle, outputPath, configuredColumns, configuredReadingMethod, configuredThicknessType, configuredBackside, maxSheets);
                uint closeAfterMark = SkDv_Close(handle);
                Console.WriteLine("close_status=0x" + closeAfterMark.ToString("X8"));
                return markReadResult;
            }

            uint closeStatus = SkDv_Close(handle);
            Console.WriteLine("close_status=0x" + closeStatus.ToString("X8"));

            return 0;
        }
        catch (BadImageFormatException ex)
        {
            Console.WriteLine("error=bad_image_format message=" + ex.Message);
            return 30;
        }
        catch (DllNotFoundException ex)
        {
            Console.WriteLine("error=dll_not_found message=" + ex.Message);
            return 31;
        }
        catch (EntryPointNotFoundException ex)
        {
            Console.WriteLine("error=entry_point_not_found message=" + ex.Message);
            return 32;
        }
        catch (Exception ex)
        {
            Console.WriteLine("error=unexpected type=" + ex.GetType().FullName + " message=" + ex.Message);
            return 33;
        }
    }

    private static int RunMarkRead(uint handle, string outputPath, int columns, int readingMethod, int thicknessType, bool backsideReading, int maxSheets)
    {
        // --- MODE: Get → suppress TM/DF/LeftSkew warnings → Set --------
        // Vendor sample (Form1.vb) always does GetMode + SetMode before
        // SetMarkConf.  Without this, the device may reject feeds with R4
        // Timing Mark Error depending on its current mode state.
        var mode = new SK_DV_SR3500_MODE();
        uint getModeStatus = SkDv_GetMode(handle, ref mode);
        Console.WriteLine("get_mode_status=0x" + getModeStatus.ToString("X8"));
        Console.WriteLine("mode_warn_before=0x" + mode.dwDisableWarning.ToString("X8"));
        // Suppress timing-mark, double-feed, and left-skew errors so the
        // device feeds forms even if edge timing marks are weak or absent
        // (common with Direct reading method on certain form stocks).
        mode.dwDisableWarning |= SkdvWarnTmError | SkdvWarnDfError | SkdvWarnLeftSkew;
        uint setModeStatus = SkDv_SetMode(handle, ref mode);
        Console.WriteLine("set_mode_status=0x" + setModeStatus.ToString("X8"));
        Console.WriteLine("mode_warn_after=0x" + mode.dwDisableWarning.ToString("X8"));

        // --- MARK CONF -------------------------------------------------
        var markConf = new SK_DV_SR3500MARK_CONF();
        uint markConfStatus = SkDv_GetMarkConf(handle, ref markConf);
        Console.WriteLine("get_mark_conf_status=0x" + markConfStatus.ToString("X8"));
        Console.WriteLine(
            "mark_conf_device_original="
            + "backside=" + markConf.iBackSideReading
            + ",columns=" + markConf.iColumns
            + ",method=" + markConf.iReadingMethod
            + ",ctrl_multiple=" + markConf.iCtrlMultiple
            + ",thickness=" + markConf.iThicknessType);
        markConf.iBackSideReading = backsideReading ? 1 : 0;
        markConf.iColumns = Clamp(columns, 1, 48);
        markConf.iReadingMethod = Clamp(readingMethod, 1, 6);
        markConf.iThicknessType = Clamp(thicknessType, 0, 5);
        // iCtrlMultiple (timing spacing) only relevant for Control reading
        // methods (1, 2). For Direct (3) and others, leave device value.
        if (readingMethod <= 2)
        {
            if (markConf.iCtrlMultiple < 1 || markConf.iCtrlMultiple > 9)
            {
                markConf.iCtrlMultiple = 1;
            }
        }

        uint setMarkConfStatus = SkDv_SetMarkConf(handle, ref markConf);
        Console.WriteLine("set_mark_conf_status=0x" + setMarkConfStatus.ToString("X8"));
        Console.WriteLine(
            "mark_conf_applied="
            + "backside=" + markConf.iBackSideReading
            + ",columns=" + markConf.iColumns
            + ",method=" + markConf.iReadingMethod
            + ",ctrl_multiple=" + markConf.iCtrlMultiple
            + ",thickness=" + markConf.iThicknessType);

        if (setMarkConfStatus != SkdvSuccess)
        {
            return 43;
        }

        // Pre-read safety: check if a form is stuck in the transport path.
        // INPS(0x08)=input sensor, RDPS(0x10)=read sensor, OUTPS(0x20)=output sensor.
        // These indicate paper IN the transport, not the hopper.
        // UPPS(0x02)/PS0(0x04) = hopper paper presence — NOT transport stuck.
        uint preSensor = 0;
        uint preSensorStatus = SkDv_ReqGetSensor(handle, ref preSensor);
        Console.WriteLine("pre_read_sensor_status=0x" + preSensorStatus.ToString("X8"));
        Console.WriteLine("pre_read_sensor_bits=0x" + preSensor.ToString("X8"));
        bool transportStuck = preSensorStatus == SkdvSuccess && (preSensor & 0x38) != 0;
        Console.WriteLine("pre_read_transport_stuck=" + transportStuck.ToString().ToLower());
        if (transportStuck)
        {
            uint ejectStatus = SkDv_ReqEjectForm(handle, SkdvEjectMain);
            Console.WriteLine("pre_read_eject_status=0x" + ejectStatus.ToString("X8"));
            // After eject, re-init to clear device state
            uint reInitStatus = SkDv_ReqInit(handle);
            Console.WriteLine("pre_read_reinit_status=0x" + reInitStatus.ToString("X8"));
        }

        Directory.CreateDirectory(Path.GetDirectoryName(outputPath) ?? AppDomain.CurrentDomain.BaseDirectory);
        using (var writer = new StreamWriter(outputPath, false))
        {
            int sheetIndex = 0;
            while (maxSheets <= 0 || sheetIndex < maxSheets)
            {
                uint feedStatus = SkDv_ReqFeedMarkSheet(handle);
                Console.WriteLine("feed_mark_sheet_status=0x" + feedStatus.ToString("X8"));

                if ((feedStatus & SkdvDeviceStaMask) == SkdvDeviceStQ1)
                {
                    Console.WriteLine("device_status=hopper_empty");
                    if (sheetIndex == 0)
                    {
                        return 40;
                    }
                    break;
                }

                if (feedStatus != SkdvSuccess)
                {
                    if (sheetIndex > 0)
                    {
                        // At least one sheet was already read successfully.
                        // Treat feed error as end-of-batch so partial results are preserved.
                        Console.WriteLine("feed_partial_end=0x" + feedStatus.ToString("X8"));
                        // Eject the failed form + ReqInit so device is clean for next call
                        uint feedEjectStatus = SkDv_ReqEjectForm(handle, SkdvEjectMain);
                        Console.WriteLine("feed_partial_eject_status=0x" + feedEjectStatus.ToString("X8"));
                        uint partialReInit = SkDv_ReqInit(handle);
                        Console.WriteLine("feed_partial_reinit_status=0x" + partialReInit.ToString("X8"));
                        break;
                    }
                    // First sheet failed. Full recovery: eject → ReqInit → reconfigure → retry.
                    Console.WriteLine("feed_first_fail_recovery=true");
                    uint eject1 = SkDv_ReqEjectForm(handle, SkdvEjectMain);
                    Console.WriteLine("recovery_eject_status=0x" + eject1.ToString("X8"));
                    uint reInit1 = SkDv_ReqInit(handle);
                    Console.WriteLine("recovery_reinit_status=0x" + reInit1.ToString("X8"));
                    if (reInit1 != SkdvSuccess)
                    {
                        return 41;
                    }
                    // Re-apply mode + mark conf after init
                    var recoveryMode = new SK_DV_SR3500_MODE();
                    SkDv_GetMode(handle, ref recoveryMode);
                    recoveryMode.dwDisableWarning |= SkdvWarnTmError | SkdvWarnDfError | SkdvWarnLeftSkew;
                    SkDv_SetMode(handle, ref recoveryMode);
                    var recoveryConf = new SK_DV_SR3500MARK_CONF();
                    SkDv_GetMarkConf(handle, ref recoveryConf);
                    recoveryConf.iBackSideReading = backsideReading ? 1 : 0;
                    recoveryConf.iColumns = Clamp(columns, 1, 48);
                    recoveryConf.iReadingMethod = Clamp(readingMethod, 1, 6);
                    recoveryConf.iThicknessType = Clamp(thicknessType, 0, 5);
                    SkDv_SetMarkConf(handle, ref recoveryConf);
                    Console.WriteLine("recovery_reconf_done=true");
                    feedStatus = SkDv_ReqFeedMarkSheet(handle);
                    Console.WriteLine("recovery_feed_status=0x" + feedStatus.ToString("X8"));
                    if (feedStatus != SkdvSuccess)
                    {
                        return 41;
                    }
                }

                var frontInfo = new SK_DV_MARK_INFO();
                var frontMarks = new byte[48 * 155];
                int frontBufferSize = frontMarks.Length;
                uint frontStatus = SkDv_ReqGetMarks(handle, 0, ref frontInfo, frontMarks, ref frontBufferSize);
                Console.WriteLine("get_front_marks_status=0x" + frontStatus.ToString("X8"));
                Console.WriteLine("front_info=type=" + frontInfo.iType + ",rows=" + frontInfo.iRows + ",columns=" + frontInfo.iColumns + ",buffer_size=" + frontBufferSize);

                if (frontStatus != SkdvSuccess)
                {
                    return 42;
                }

                sheetIndex += 1;
                writer.WriteLine("[sheet_" + sheetIndex + "]");
                writer.WriteLine("front_rows=" + frontInfo.iRows);
                writer.WriteLine("front_columns=" + frontInfo.iColumns);
                writer.WriteLine("front_type=" + frontInfo.iType);
                WriteMarkMatrix(writer, frontInfo, frontMarks, frontBufferSize);
                writer.WriteLine("[/sheet_" + sheetIndex + "]");
            }
        }

        Console.WriteLine("mark_output=" + outputPath);
        return 0;
    }

    private static int Clamp(int value, int min, int max)
    {
        if (value < min)
        {
            return min;
        }
        if (value > max)
        {
            return max;
        }
        return value;
    }

    private static int SafeParseInt(string text, int defaultValue)
    {
        int parsed;
        return int.TryParse(text, out parsed) ? parsed : defaultValue;
    }

    private static void WriteMarkMatrix(StreamWriter writer, SK_DV_MARK_INFO info, byte[] marks, int bufferSize)
    {
        int rows = info.iRows > 0 ? info.iRows : 0;
        int columns = info.iColumns > 0 ? info.iColumns : 0;
        int expected = rows * columns;
        int usable = Math.Min(bufferSize, Math.Min(expected > 0 ? expected : marks.Length, marks.Length));
        writer.WriteLine("front_marks=");

        if (rows <= 0 || columns <= 0 || usable <= 0)
        {
            writer.WriteLine("<empty>");
            return;
        }

        for (int row = 0; row < rows; row++)
        {
            int rowStart = row * columns;
            if (rowStart >= usable)
            {
                break;
            }

            int rowEnd = Math.Min(rowStart + columns, usable);
            for (int index = rowStart; index < rowEnd; index++)
            {
                if (index > rowStart)
                {
                    writer.Write(',');
                }

                writer.Write(marks[index]);
            }

            writer.WriteLine();
        }
    }
}