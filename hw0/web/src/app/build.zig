const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    var options = b.addOptions();
    // ip and port
    const ip = "0.0.0.0";
    options.addOption([]const u8, "ip", ip);
    const port: u16 = 1337;
    options.addOption(@TypeOf(port), "port", port);
    // generate tokens before compiling main.zig
    var buf: [64]u8 = undefined;
    std.crypto.random.bytes(&buf);
    const admin_token = std.fmt.bytesToHex(buf, .lower);
    options.addOption(@TypeOf(admin_token), "admin_token", admin_token);
    std.crypto.random.bytes(&buf);
    const backdoor_token = std.fmt.bytesToHex(buf, .lower);
    options.addOption(@TypeOf(backdoor_token), "backdoor_token", backdoor_token);

    const exe = b.addExecutable(.{
        .name = "server",
        .root_module = b.createModule(.{
            .root_source_file = b.path("src/main.zig"),
            .target = target,
            .optimize = optimize,
            .link_libc = false,
        }),
    });
    exe.root_module.addOptions("configs", options);

    b.installArtifact(exe);

    const run_step = b.step("run", "Run the app");

    const run_cmd = b.addRunArtifact(exe);
    run_step.dependOn(&run_cmd.step);

    run_cmd.step.dependOn(b.getInstallStep());

    if (b.args) |args| {
        run_cmd.addArgs(args);
    }
}
