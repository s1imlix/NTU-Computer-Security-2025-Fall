const std = @import("std");
const builtin = @import("builtin");
const configs = @import("configs");

pub fn main() !void {
    std.log.info("admin token: {s}", .{configs.admin_token});
    std.log.info("backdoor token: {s}", .{configs.backdoor_token});
    var da = std.heap.DebugAllocator(.{}){};
    const allocator = if (builtin.mode == .Debug) da.allocator() else std.heap.smp_allocator;
    defer {
        if (builtin.mode == .Debug) _ = da.deinit();
    }
    const addr = try std.net.Address.parseIp4(configs.ip, configs.port);
    var server = try addr.listen(std.net.Address.ListenOptions{ .reuse_address = true });
    defer server.deinit();

    std.log.info("Start HTTP server at http://{s}:{d}", .{ configs.ip, configs.port });

    while (true) {
        const conn = server.accept() catch |err| {
            std.log.err("Failed to accept connection: {s}", .{@errorName(err)});
            continue;
        };
        _ = std.Thread.spawn(.{}, accept, .{ allocator, conn }) catch |err| {
            std.log.err("Unable to spawn connection thread: {s}", .{@errorName(err)});
            conn.stream.close();
            continue;
        };
    }
}

fn passBackdoorTokenCheck(req: *std.http.Server.Request) bool {
    var it = req.iterateHeaders();
    while (it.next()) |h| {
        if (std.mem.eql(u8, h.name, "X-Backdoor-Token") and std.mem.eql(u8, &configs.backdoor_token, h.value)) {
            return true;
        }
    }
    return false;
}

fn allocGetAdminToken(allocator: std.mem.Allocator, req: *std.http.Server.Request) !?[]u8 {
    var it = req.iterateHeaders();
    while (it.next()) |h| {
        if (std.mem.eql(u8, h.name, "Cookie") and h.value.len > 0) {
            const key = "admin_token=";
            if (std.mem.indexOf(u8, h.value, key)) |pos| {
                const rest = h.value[pos + key.len ..];
                const end = std.mem.indexOfScalar(u8, rest, ';') orelse rest.len;
                const token = rest[0..end];
                return try allocator.dupe(u8, token);
            } else {
                return null;
            }
        }
    }
    return null;
}

fn handleRequest(allocator: std.mem.Allocator, req: *std.http.Server.Request) !void {
    const method = req.head.method;
    const target = req.head.target;
    if (method == .GET and std.mem.eql(u8, target, "/")) {
        try req.respond(@embedFile("static/index.html"), std.http.Server.Request.RespondOptions{
            .keep_alive = false,
            .extra_headers = &.{
                .{ .name = "content-type", .value = "text/html" },
            },
        });
    } else if (method == .POST and std.mem.eql(u8, target, "/give_me_flag")) {
        try req.respond("ok, listen carefully", std.http.Server.Request.RespondOptions{
            .status = .found,
            .keep_alive = false,
            .extra_headers = &.{
                .{ .name = "location", .value = "/give_me_flag" },
                .{ .name = "set-cookie", .value = "admin_token=; max-age=1; HttpOnly" },
            },
        });
    } else if (method == .GET and std.mem.eql(u8, target, "/give_me_flag")) {
        // Some ideas are from @t510599, thanks!
        if (try allocGetAdminToken(allocator, req)) |current| {
            defer allocator.free(current);
            std.log.info("len: {d}, value: {s}", .{ current.len, current });
            if (std.mem.eql(u8, &configs.admin_token, current)) {
                // Use these tokens to get the flag!
                try req.respond(&configs.backdoor_token, std.http.Server.Request.RespondOptions{
                    .keep_alive = false,
                    .extra_headers = &.{
                        .{ .name = "location", .value = "/" },
                        .{ .name = "set-cookie", .value = "admin_token=; max-age=0; HttpOnly" },
                    },
                });
                return;
            } else if (std.mem.startsWith(u8, &configs.admin_token, current)) {
                const new_cookie = try std.mem.concat(allocator, u8, &[_][]const u8{
                    "admin_token=",
                    configs.admin_token[0 .. current.len + 1],
                    "; max-age=1; HttpOnly",
                });
                defer allocator.free(new_cookie);
                std.log.info("yes", .{});
                try req.respond("yes", std.http.Server.Request.RespondOptions{
                    .status = .found,
                    .keep_alive = false,
                    .extra_headers = &.{
                        .{ .name = "location", .value = "/give_me_flag" },
                        .{ .name = "set-cookie", .value = new_cookie },
                    },
                });
                return;
            }
        }
        try req.respond("nope", std.http.Server.Request.RespondOptions{
            .status = .found,
            .keep_alive = false,
            .extra_headers = &.{
                .{ .name = "location", .value = "/" },
                .{ .name = "set-cookie", .value = "token=; max-age=0; HttpOnly" },
            },
        });
    } else if (method == .POST and std.mem.eql(u8, target, "/backdoor/../(^_^)/|>#")) {
        // Check Header
        if (!passBackdoorTokenCheck(req)) {
            std.log.err("Backdoor token check failed", .{});
            try req.respond("????", std.http.Server.Request.RespondOptions{
                .status = .bad_request,
                .keep_alive = false,
            });
            return;
        }

        // Check cookie
        if (try allocGetAdminToken(allocator, req)) |token| {
            defer allocator.free(token);
            if (!std.mem.eql(u8, &configs.admin_token, token)) {
                std.log.err("Admin token check Failed", .{});
                try req.respond("!!!!", std.http.Server.Request.RespondOptions{
                    .status = .bad_request,
                    .keep_alive = false,
                });
                return;
            }
        }

        // Parse command
        var body_buf: [1024]u8 = undefined;
        var body_reader = req.readerExpectNone(&.{});
        const body_size = try body_reader.readSliceShort(&body_buf);
        const Commandline = struct { cmd: []u8 };
        const parsed = std.json.parseFromSlice(Commandline, allocator, body_buf[0..body_size], .{}) catch |err| {
            std.log.err("Unable to parse JSON: {s}", .{@errorName(err)});
            try req.respond("Invalid request", std.http.Server.Request.RespondOptions{
                .status = .bad_request,
                .keep_alive = false,
            });
            return;
        };
        defer parsed.deinit();

        // Try to get the flag!
        // Note: All environment variables will be passed into the sandbox
        var child = std.process.Child.init(&[_][]const u8{
            "nsjail",
            "-Mo",
            "-e",
            "-t",
            "3",
            "--disable_clone_newnet",
            "--rlimit_as",
            "32",
            "--chroot",
            "/chroot",
            "--",
            "/bin/bash",
            "-c",
            parsed.value.cmd,
        }, allocator);
        child.stdout_behavior = .Ignore;
        child.stderr_behavior = .Ignore;
        try child.spawn();
        _ = try child.wait();

        try req.respond("Command executed!", std.http.Server.Request.RespondOptions{
            .keep_alive = false,
        });
    } else {
        try req.respond("404", std.http.Server.Request.RespondOptions{
            .status = .not_found,
            .keep_alive = false,
            .extra_headers = &.{
                .{ .name = "content-type", .value = "text/plain" },
            },
        });
    }
}

fn accept(allocator: std.mem.Allocator, conn: std.net.Server.Connection) !void {
    defer conn.stream.close();
    var recv_buf: [4096]u8 = undefined;
    var send_buf: [4096]u8 = undefined;
    var conn_reader = conn.stream.reader(&recv_buf);
    var conn_writer = conn.stream.writer(&send_buf);
    var server = std.http.Server.init(conn_reader.interface(), &conn_writer.interface);

    var req = server.receiveHead() catch |err| switch (err) {
        error.HttpConnectionClosing => return,
        else => return err,
    };
    std.log.info("{s} {s} {s}", .{
        @tagName(req.head.method),
        req.head.target,
        @tagName(req.head.version),
    });
    try handleRequest(allocator, &req);
}
