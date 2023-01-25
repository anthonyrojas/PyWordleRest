from fastapi import Request, HTTPException, status


async def validate_token(req: Request):
    try:
        authentication = req.headers["Authentication"]
        if not str.startswith(authentication, "Bearer"):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, {
                "message": "Authentication token not found!"
            })
        token = authentication.split(" ")[1]
        auth_provider = req.state.auth_provider
        cognito_user = auth_provider.verify_token(token)
        username = cognito_user["Username"]
        req.state.username = username
        return True
    except Exception as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, {
            "message": "Unauthorized! Failed to validate token.",
            "errorMessage": str(e)
        })

