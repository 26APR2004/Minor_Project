"""
Leave Management MCP Server using FastMCP (with employee names).
Run with:
    uv run server leave_mcp_server stdio
"""

from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("LeaveManagement")

# In-memory data store (for demo)
employees = {
    "emp101": {"name": "Sujal Mane", "balance": 10},
    "emp102": {"name": "Riya Sharma", "balance": 7},
    "emp103": {"name": "Amit Verma", "balance": 15}
}

leave_requests = {}  # request_id -> request data


# ----------------- TOOLS -----------------

@mcp.tool()
def apply_leave(employee_id: str, days: int, reason: str) -> str:
    """Apply for leave"""
    if employee_id not in employees:
        return f"❌ Employee {employee_id} not found."

    if days > employees[employee_id]["balance"]:
        return f"❌ Insufficient leave balance. {employees[employee_id]['name']} has {employees[employee_id]['balance']} days left."

    request_id = f"REQ{len(leave_requests) + 1}"
    leave_requests[request_id] = {
        "employee_id": employee_id,
        "employee_name": employees[employee_id]["name"],
        "days": days,
        "reason": reason,
        "status": "Pending"
    }
    return f"✅ {employees[employee_id]['name']} (ID: {employee_id}) submitted leave request {request_id}."


@mcp.tool()
def check_status(request_id: str) -> str:
    """Check the status of a leave request"""
    if request_id not in leave_requests:
        return f"❌ Request {request_id} not found."
    req = leave_requests[request_id]
    return (f"Request {request_id}: {req['status']} | "
            f"{req['employee_name']} ({req['employee_id']}) requested {req['days']} days for '{req['reason']}'.")


@mcp.tool()
def approve_leave(request_id: str, manager_id: str, manager_name: str) -> str:
    """Approve a leave request (manager use only)"""
    if request_id not in leave_requests:
        return f"❌ Request {request_id} not found."

    req = leave_requests[request_id]
    req["status"] = "Approved"
    employees[req["employee_id"]]["balance"] -= req["days"]

    return (f"✅ Request {request_id} approved by Manager {manager_name} (ID: {manager_id}). "
            f"{req['employee_name']} now has {employees[req['employee_id']]['balance']} days remaining.")


@mcp.tool()
def reject_leave(request_id: str, manager_id: str, manager_name: str, reason: str) -> str:
    """Reject a leave request (manager use only)"""
    if request_id not in leave_requests:
        return f"❌ Request {request_id} not found."

    req = leave_requests[request_id]
    req["status"] = f"Rejected ({reason})"

    return (f"❌ Request {request_id} rejected by Manager {manager_name} (ID: {manager_id}). "
            f"Reason: {reason}. Employee: {req['employee_name']} ({req['employee_id']}).")


# ----------------- RESOURCES -----------------

@mcp.resource("leavebalance://{employee_id}")
def get_balance(employee_id: str) -> str:
    """Check leave balance for an employee"""
    emp = employees.get(employee_id, None)
    if emp is None:
        return f"❌ Employee {employee_id} not found."
    return f"{emp['name']} ({employee_id}) has {emp['balance']} leave days remaining."


# ----------------- PROMPTS -----------------

@mcp.prompt()
def leave_approval_message(employee_name: str, employee_id: str, status: str, manager_name: str) -> str:
    """Generate a message for leave approval/rejection"""
    if status.lower() == "approved":
        return f"Dear {employee_name} ({employee_id}), your leave request has been APPROVED by Manager {manager_name}."
    else:
        return f"Dear {employee_name} ({employee_id}), your leave request has been REJECTED by Manager {manager_name}. Please contact HR."


# ----------------- RUN SERVER -----------------
if __name__ == "__main__":
    mcp.run()
