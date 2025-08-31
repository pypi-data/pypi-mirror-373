permit (
    principal,
    action == Action::"Workflow::List",
    resource
);

permit (
    principal,
    action == Action::"Workflow::ViewDetails",
    resource
);

permit (
    principal,
    action == Action::"Workflow::Run",
    resource
);

permit (
    principal,
    action == Action::"Workflow::Cancel",
    resource
);

permit (
    principal,
    action == Action::"Agent::List",
    resource
);

permit (
    principal,
    action == Action::"Agent::ViewDetails",
    resource
);

permit (
    principal,
    action == Action::"Agent::Run",
    resource
);

permit (
    principal,
    action == Action::"Agent::Update",
    resource
);

permit (
    principal,
    action == Action::"Agent::Simulate",
    resource
);

permit (
    principal in Role::"admin",
    action == Action::"Rule::Update",
    resource
);

permit (
    principal,
    action == Action::"Rule::List",
    resource
);

permit (
    principal,
    action == Action::"Rule::ViewDetails",
    resource
);

permit (
    principal,
    action == Action::"Rule::Simulate",
    resource
);