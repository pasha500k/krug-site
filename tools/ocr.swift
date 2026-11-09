import Foundation
import Vision
import ImageIO
guard CommandLine.arguments.count == 2 else { exit(2) }
let input = URL(fileURLWithPath: CommandLine.arguments[1])
let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
let supported = (try? request.supportedRecognitionLanguages()) ?? []
request.recognitionLanguages = ["ru-RU", "en-US"].filter { supported.contains($0) }
request.usesLanguageCorrection = false
do {
    try VNImageRequestHandler(url: input, options: [:]).perform([request])
    for observation in request.results ?? [] {
        if let candidate = observation.topCandidates(1).first { print(candidate.string) }
    }
} catch {
    fputs("\(error)\n", stderr)
    exit(1)
}
