// Instant option price with NEURAX Edge, from Excel (Power Query).
let
    Body = Json.FromValue([
        function = "option.price@1",
        input = [spot = 100, strike = 105, rate = 0.03, volatility = 0.2, years = 1, type = "call"],
        region = "EUROPE"
    ]),
    Response = Json.Document(Web.Contents("https://api.neuraxcopute.it/v1/edge/run",
        [Headers = [Authorization = "Bearer " & NeuraxKey, #"Content-Type" = "application/json"],
         Content = Body])),
    Result = Record.ToTable(Response[output])
in
    Result
