export default defineEventHandler(async (event) => {
    const postBody = await readBody(event)
    const job = postBody.job
    try {
        const resp: Object = await $fetch("http://127.0.0.1:8000/generate", { body: { "job_description": job }, method: "POST" })
        // Use if you have an AWS account -const upload: string = await $fetch("http://127.0.0.1:8000/upload", { body: resp, method: "POST" })
        let packaged_response = { "data": resp, "url": "" }
        console.log(resp)
        /* if (upload) {
            packaged_response['url'] = upload
        } */
        return packaged_response
    } catch {
        return ""
    }


})